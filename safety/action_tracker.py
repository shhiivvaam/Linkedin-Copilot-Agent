"""
Action Tracker - Prevents duplicate actions
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from loguru import logger


class ActionTracker:
    """Tracks actions to prevent duplicates"""
    
    def __init__(self, db_path: str = './sessions/actions.db'):
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Initialize database tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Track contacted recruiters
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS contacted_recruiters (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                recruiter_url TEXT UNIQUE,
                recruiter_name TEXT,
                company TEXT,
                contacted_at TIMESTAMP,
                message_sent BOOLEAN DEFAULT 0
            )
        ''')
        
        # Track applied jobs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applied_jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT UNIQUE,
                job_title TEXT,
                company TEXT,
                applied_at TIMESTAMP,
                status TEXT DEFAULT 'pending'
            )
        ''')
        
        # Track all actions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS action_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action_type TEXT,
                target_url TEXT,
                target_name TEXT,
                timestamp TIMESTAMP,
                status TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def is_recruiter_contacted(self, recruiter_url: str) -> bool:
        """Check if recruiter has been contacted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT COUNT(*) FROM contacted_recruiters WHERE recruiter_url = ?',
            (recruiter_url,)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def record_recruiter_contact(self, recruiter_url: str, recruiter_name: str, 
                                 company: str, message_sent: bool = False):
        """Record that a recruiter was contacted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO contacted_recruiters 
                (recruiter_url, recruiter_name, company, contacted_at, message_sent)
                VALUES (?, ?, ?, ?, ?)
            ''', (recruiter_url, recruiter_name, company, datetime.now(), message_sent))
            
            conn.commit()
            logger.info(f"Recorded contact with recruiter: {recruiter_name}")
        except Exception as e:
            logger.error(f"Failed to record recruiter contact: {e}")
        finally:
            conn.close()
    
    def is_job_applied(self, job_url: str) -> bool:
        """Check if job has been applied to"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute(
            'SELECT COUNT(*) FROM applied_jobs WHERE job_url = ?',
            (job_url,)
        )
        
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    
    def record_job_application(self, job_url: str, job_title: str, 
                               company: str, status: str = 'pending'):
        """Record that a job application was submitted"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR IGNORE INTO applied_jobs 
                (job_url, job_title, company, applied_at, status)
                VALUES (?, ?, ?, ?, ?)
            ''', (job_url, job_title, company, datetime.now(), status))
            
            conn.commit()
            logger.info(f"Recorded job application: {job_title} at {company}")
        except Exception as e:
            logger.error(f"Failed to record job application: {e}")
        finally:
            conn.close()
    
    def log_action(self, action_type: str, target_url: str, target_name: str,
                   status: str, details: Optional[str] = None):
        """Log any action"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO action_log 
                (action_type, target_url, target_name, timestamp, status, details)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (action_type, target_url, target_name, datetime.now(), status, details))
            
            conn.commit()
        except Exception as e:
            logger.error(f"Failed to log action: {e}")
        finally:
            conn.close()
    
    def get_daily_summary(self, date: Optional[datetime] = None) -> Dict:
        """Get summary of actions for a day"""
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime('%Y-%m-%d')
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Count contacted recruiters today
        cursor.execute('''
            SELECT COUNT(*) FROM contacted_recruiters 
            WHERE DATE(contacted_at) = ?
        ''', (date_str,))
        recruiters_contacted = cursor.fetchone()[0]
        
        # Count applied jobs today
        cursor.execute('''
            SELECT COUNT(*) FROM applied_jobs 
            WHERE DATE(applied_at) = ?
        ''', (date_str,))
        jobs_applied = cursor.fetchone()[0]
        
        # Get recent actions
        cursor.execute('''
            SELECT action_type, target_name, status, timestamp 
            FROM action_log 
            WHERE DATE(timestamp) = ?
            ORDER BY timestamp DESC
            LIMIT 50
        ''', (date_str,))
        recent_actions = cursor.fetchall()
        
        conn.close()
        
        return {
            'date': date_str,
            'recruiters_contacted': recruiters_contacted,
            'jobs_applied': jobs_applied,
            'recent_actions': recent_actions,
        }

