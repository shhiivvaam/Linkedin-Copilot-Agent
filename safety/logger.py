"""
Safety Logger - Comprehensive logging system
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import sys


class SafetyLogger:
    """Enhanced logging with file rotation and daily summaries"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        log_config = config.get('logging', {})
        self.log_dir = Path(log_config.get('log_dir', './logs'))
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.level = log_config.get('level', 'INFO')
        self.daily_summary = log_config.get('daily_summary', True)
        self.detailed_logs = log_config.get('detailed_logs', True)
        
        self._setup_logger()
    
    def _setup_logger(self):
        """Configure loguru logger"""
        # Remove default handler
        logger.remove()
        
        # Add console handler
        logger.add(
            sys.stdout,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
            level=self.level,
            colorize=True,
        )
        
        # Add file handler with rotation
        log_file = self.log_dir / "copilot_{time:YYYY-MM-DD}.log"
        logger.add(
            log_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level=self.level,
            rotation="00:00",  # Rotate at midnight
            retention="30 days",
            compression="zip",
        )
        
        # Add error file handler
        error_file = self.log_dir / "errors_{time:YYYY-MM-DD}.log"
        logger.add(
            error_file,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function} - {message}",
            level="ERROR",
            rotation="00:00",
            retention="90 days",
        )
    
    def log_action(self, action_type: str, details: Dict[str, Any], 
                   status: str = 'success'):
        """Log a specific action"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'action_type': action_type,
            'status': status,
            'details': details,
        }
        
        if status == 'success':
            logger.info(f"{action_type}: {json.dumps(details)}")
        elif status == 'warning':
            logger.warning(f"{action_type}: {json.dumps(details)}")
        else:
            logger.error(f"{action_type}: {json.dumps(details)}")
        
        # Save to detailed log file if enabled
        if self.detailed_logs:
            detailed_log_file = self.log_dir / "detailed_actions.jsonl"
            with open(detailed_log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
    
    def log_error(self, error: Exception, context: Optional[Dict[str, Any]] = None):
        """Log an error with context"""
        error_details = {
            'error_type': type(error).__name__,
            'error_message': str(error),
            'context': context or {},
        }
        
        logger.exception(f"Error occurred: {error_details}")
        self.log_action('error', error_details, status='error')
    
    def generate_daily_summary(self, summary_data: Dict[str, Any]):
        """Generate and save daily summary"""
        if not self.daily_summary:
            return
        
        summary_file = self.log_dir / f"summary_{datetime.now().strftime('%Y-%m-%d')}.json"
        
        summary = {
            'date': datetime.now().isoformat(),
            'summary': summary_data,
        }
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info("Daily summary generated")
        
        # Also print summary
        logger.info("=" * 50)
        logger.info("DAILY SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Recruiters Contacted: {summary_data.get('recruiters_contacted', 0)}")
        logger.info(f"Jobs Applied: {summary_data.get('jobs_applied', 0)}")
        logger.info(f"Actions Today: {summary_data.get('actions_today', 0)}")
        logger.info("=" * 50)

