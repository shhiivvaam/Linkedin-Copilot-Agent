"""
Rate Limiting - Prevents excessive actions
"""

from datetime import datetime, timedelta
from typing import Dict, List, Optional
from loguru import logger
import time
import random


class RateLimiter:
    """Manages rate limiting for actions"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.max_actions_per_day = config.get('safety', {}).get('max_actions_per_day', 20)
        self.min_delay = config.get('safety', {}).get('min_delay_between_actions', 300)
        self.max_delay = config.get('safety', {}).get('max_delay_between_actions', 900)
        
        self.daily_actions: List[datetime] = []
        self.last_action_time: Optional[datetime] = None
    
    def can_perform_action(self) -> bool:
        """Check if action can be performed"""
        now = datetime.now()
        
        # Reset daily actions if it's a new day
        self.daily_actions = [
            action for action in self.daily_actions
            if (now - action).days < 1
        ]
        
        # Check daily limit
        if len(self.daily_actions) >= self.max_actions_per_day:
            logger.warning(f"Daily action limit reached ({self.max_actions_per_day})")
            return False
        
        # Check delay since last action
        if self.last_action_time:
            time_since_last = (now - self.last_action_time).total_seconds()
            min_delay = self.min_delay
            
            if time_since_last < min_delay:
                wait_time = min_delay - time_since_last
                logger.info(f"Rate limit: waiting {wait_time:.1f} seconds")
                time.sleep(wait_time)
        
        return True
    
    def record_action(self):
        """Record that an action was performed"""
        now = datetime.now()
        self.daily_actions.append(now)
        self.last_action_time = now
        
        # Add random delay before next action
        delay = self._get_random_delay()
        logger.debug(f"Action recorded. Next action allowed after {delay:.1f} seconds")
    
    def _get_random_delay(self) -> float:
        """Get random delay between min and max"""
        return random.uniform(self.min_delay, self.max_delay)
    
    def get_daily_stats(self) -> Dict:
        """Get statistics for today"""
        now = datetime.now()
        today_actions = [
            action for action in self.daily_actions
            if (now - action).days < 1
        ]
        
        return {
            'actions_today': len(today_actions),
            'max_actions': self.max_actions_per_day,
            'remaining': self.max_actions_per_day - len(today_actions),
            'last_action': self.last_action_time.isoformat() if self.last_action_time else None,
        }
    
    def wait_for_next_action(self):
        """Wait for the appropriate delay before next action"""
        if self.last_action_time:
            delay = self._get_random_delay()
            time.sleep(delay)

