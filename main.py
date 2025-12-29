"""
LinkedIn Job Outreach & Application Copilot
Main orchestrator that coordinates all components
"""

import yaml
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger

from browser_automation import BrowserManager
from recruiter_discovery import RecruiterSearch, RecruiterRanker
from messaging import MessageGenerator, MessageSender
from job_discovery import JobSearch, JobApplicator
from resume import ResumeParser, RequirementMatcher
from safety import RateLimiter, ActionTracker, SafetyLogger


class LinkedInCopilot:
    """Main copilot orchestrator"""
    
    def __init__(self, config_path: str = 'config.yaml'):
        """Initialize copilot with configuration"""
        self.config = self._load_config(config_path)
        self.user_profile = self.config.get('profile', {})
        
        # Initialize safety systems
        self.rate_limiter = RateLimiter(self.config)
        self.action_tracker = ActionTracker()
        self.safety_logger = SafetyLogger(self.config)
        
        # Initialize browser
        self.browser_manager = BrowserManager(self.config)
        self.page = None
        
        # Initialize resume parser
        resume_path = self.user_profile.get('resume_path', '')
        self.resume_parser = ResumeParser(resume_path, self.user_profile)
        self.resume_data = self.resume_parser.parse()
        
        logger.info("LinkedIn Copilot initialized")
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        if not os.path.exists(config_path):
            logger.error(f"Configuration file not found: {config_path}")
            logger.info("Please copy config.example.yaml to config.yaml and fill in your details")
            sys.exit(1)
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        # Override with environment variables if present
        if os.getenv('LINKEDIN_EMAIL'):
            config['linkedin']['email'] = os.getenv('LINKEDIN_EMAIL')
        if os.getenv('LINKEDIN_PASSWORD'):
            config['linkedin']['password'] = os.getenv('LINKEDIN_PASSWORD')
        
        return config
    
    def start(self):
        """Start the copilot"""
        logger.info("Starting LinkedIn Copilot...")
        
        try:
            # Start browser
            self.page = self.browser_manager.start()
            
            # Login if needed
            if not self._is_logged_in():
                email = self.config['linkedin']['email']
                password = self.config['linkedin']['password']
                
                if not self.browser_manager.login(email, password):
                    logger.error("Login failed. Please check credentials or complete CAPTCHA manually.")
                    return False
            
            logger.info("Successfully logged in to LinkedIn")
            return True
            
        except Exception as e:
            logger.error(f"Error starting copilot: {e}")
            return False
    
    def _is_logged_in(self) -> bool:
        """Check if already logged in"""
        try:
            self.page.goto('https://www.linkedin.com/feed', wait_until='networkidle')
            # Check for feed elements
            feed_elements = self.page.locator('.feed-container')
            return feed_elements.count() > 0
        except Exception:
            return False
    
    def discover_recruiters(self, max_results: int = 20) -> list:
        """Discover and rank recruiters"""
        logger.info("Starting recruiter discovery...")
        
        if not self.rate_limiter.can_perform_action():
            logger.warning("Rate limit reached. Cannot discover recruiters.")
            return []
        
        try:
            # Search for recruiters
            recruiter_search = RecruiterSearch(self.page, self.config)
            recruiters = recruiter_search.search()
            
            # Rank recruiters
            ranker = RecruiterRanker(self.config)
            ranked_recruiters = ranker.rank(recruiters, self.user_profile)
            
            # Filter out already contacted
            new_recruiters = [
                r for r in ranked_recruiters[:max_results]
                if not self.action_tracker.is_recruiter_contacted(r['url'])
            ]
            
            logger.info(f"Found {len(new_recruiters)} new recruiters to contact")
            return new_recruiters
            
        except Exception as e:
            logger.error(f"Error discovering recruiters: {e}")
            return []
    
    def draft_message(self, recruiter: Dict[str, Any], 
                     job_context: Optional[Dict[str, Any]] = None) -> str:
        """Draft a personalized message for a recruiter"""
        message_generator = MessageGenerator(self.config, self.user_profile)
        message = message_generator.generate_message(recruiter, job_context)
        
        # Validate message
        is_valid, error = message_generator.validate_message(message)
        if not is_valid:
            logger.warning(f"Message validation failed: {error}")
        
        return message
    
    def send_recruiter_message(self, recruiter: Dict[str, Any], 
                              message: str, require_approval: bool = True) -> bool:
        """Send message to recruiter"""
        if not self.rate_limiter.can_perform_action():
            logger.warning("Rate limit reached. Cannot send message.")
            return False
        
        if self.action_tracker.is_recruiter_contacted(recruiter['url']):
            logger.warning(f"Recruiter already contacted: {recruiter['url']}")
            return False
        
        try:
            message_sender = MessageSender(self.page, self.config)
            require_approval = self.config.get('safety', {}).get('human_approval_required', True)
            success = message_sender.send_message(
                recruiter['url'],
                message,
                require_approval=require_approval
            )
            
            if success:
                self.action_tracker.record_recruiter_contact(
                    recruiter['url'],
                    recruiter.get('name', ''),
                    recruiter.get('company', ''),
                    message_sent=True
                )
                self.rate_limiter.record_action()
                self.safety_logger.log_action(
                    'send_message',
                    {'recruiter': recruiter['name'], 'url': recruiter['url']},
                    status='success'
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            self.safety_logger.log_error(e, {'recruiter': recruiter})
            return False
    
    def discover_jobs(self, max_results: int = 50) -> list:
        """Discover relevant jobs"""
        logger.info("Starting job discovery...")
        
        if not self.rate_limiter.can_perform_action():
            logger.warning("Rate limit reached. Cannot discover jobs.")
            return []
        
        try:
            job_search = JobSearch(self.page, self.config)
            jobs = job_search.search()
            
            # Filter out already applied
            new_jobs = [
                j for j in jobs[:max_results]
                if not self.action_tracker.is_job_applied(j['url'])
            ]
            
            logger.info(f"Found {len(new_jobs)} new jobs")
            return new_jobs
            
        except Exception as e:
            logger.error(f"Error discovering jobs: {e}")
            return []
    
    def analyze_job(self, job_url: str) -> tuple[bool, float, Dict[str, Any]]:
        """Analyze if job is a good match"""
        try:
            job_search = JobSearch(self.page, self.config)
            job_details = job_search.get_job_details(job_url)
            
            if 'error' in job_details:
                return False, 0.0, job_details
            
            # Match resume to job
            matcher = RequirementMatcher(self.resume_data)
            should_apply, match_score = matcher.should_apply(
                job_details.get('description', ''),
                min_match_score=50.0
            )
            
            job_details['match_score'] = match_score
            job_details['should_apply'] = should_apply
            
            return should_apply, match_score, job_details
            
        except Exception as e:
            logger.error(f"Error analyzing job: {e}")
            return False, 0.0, {}
    
    def apply_to_job(self, job_url: str, require_approval: bool = True) -> bool:
        """Apply to a job"""
        if not self.rate_limiter.can_perform_action():
            logger.warning("Rate limit reached. Cannot apply to job.")
            return False
        
        if self.action_tracker.is_job_applied(job_url):
            logger.warning(f"Job already applied: {job_url}")
            return False
        
        try:
            job_applicator = JobApplicator(self.page, self.config, self.resume_data)
            require_approval = self.config.get('safety', {}).get('human_approval_required', True)
            success = job_applicator.apply_to_job(job_url, require_approval=require_approval)
            
            if success:
                # Get job title for logging
                job_search = JobSearch(self.page, self.config)
                job_details = job_search.get_job_details(job_url)
                
                self.action_tracker.record_job_application(
                    job_url,
                    job_details.get('title', 'Unknown'),
                    job_details.get('company', 'Unknown'),
                    status='submitted'
                )
                self.rate_limiter.record_action()
                self.safety_logger.log_action(
                    'apply_job',
                    {'job_url': job_url, 'title': job_details.get('title', '')},
                    status='success'
                )
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            self.safety_logger.log_error(e, {'job_url': job_url})
            return False
    
    def generate_daily_summary(self):
        """Generate daily summary report"""
        summary = self.action_tracker.get_daily_summary()
        rate_stats = self.rate_limiter.get_daily_stats()
        
        summary.update(rate_stats)
        self.safety_logger.generate_daily_summary(summary)
        
        return summary
    
    def stop(self):
        """Stop the copilot"""
        logger.info("Stopping LinkedIn Copilot...")
        
        # Generate daily summary
        self.generate_daily_summary()
        
        # Close browser
        if self.browser_manager:
            self.browser_manager.close()
        
        logger.info("LinkedIn Copilot stopped")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='LinkedIn Job Outreach & Application Copilot')
    parser.add_argument('--config', default='config.yaml', help='Path to configuration file')
    parser.add_argument('--mode', choices=['recruiters', 'jobs', 'both'], default='both',
                       help='Operation mode')
    
    args = parser.parse_args()
    
    # Initialize copilot
    copilot = LinkedInCopilot(args.config)
    
    if not copilot.start():
        logger.error("Failed to start copilot")
        return
    
    try:
        if args.mode in ['recruiters', 'both']:
            # Discover recruiters
            recruiters = copilot.discover_recruiters(max_results=10)
            
            for recruiter in recruiters[:5]:  # Limit to 5 for demo
                logger.info(f"\nFound recruiter: {recruiter['name']} at {recruiter['company']}")
                
                # Draft message
                message = copilot.draft_message(recruiter)
                print(f"\n--- Drafted Message ---\n{message}\n--- End Message ---\n")
                
                # Ask for approval
                approval = input("Send this message? (y/n): ")
                if approval.lower() == 'y':
                    copilot.send_recruiter_message(recruiter, message)
                else:
                    logger.info("Message not sent")
        
        if args.mode in ['jobs', 'both']:
            # Discover jobs
            jobs = copilot.discover_jobs(max_results=20)
            
            for job in jobs[:5]:  # Limit to 5 for demo
                logger.info(f"\nFound job: {job['title']} at {job['company']}")
                
                # Analyze job
                should_apply, match_score, job_details = copilot.analyze_job(job['url'])
                logger.info(f"Match score: {match_score:.1f}%")
                
                if should_apply:
                    approval = input(f"Apply to {job['title']}? (y/n): ")
                    if approval.lower() == 'y':
                        copilot.apply_to_job(job['url'])
                    else:
                        logger.info("Application not submitted")
        
        # Generate summary
        copilot.generate_daily_summary()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error during execution: {e}")
    finally:
        copilot.stop()


if __name__ == '__main__':
    main()

