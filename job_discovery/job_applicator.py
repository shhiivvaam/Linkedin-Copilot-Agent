"""
Job Applicator - Assist with LinkedIn Easy Apply
"""

import time
import random
from typing import Dict, Any, Optional
from playwright.sync_api import Page
from loguru import logger

from browser_automation.human_like import HumanLikeBehavior


class JobApplicator:
    """Assist with job applications"""
    
    def __init__(self, page: Page, config: Dict[str, Any], resume_data: Dict[str, Any]):
        self.page = page
        self.config = config
        self.resume_data = resume_data
        self.application_config = config.get('application', {})
    
    def apply_to_job(self, job_url: str, require_approval: bool = True) -> bool:
        """Apply to a job using Easy Apply"""
        logger.info(f"Applying to job: {job_url}")
        
        try:
            # Navigate to job page
            self.page.goto(job_url, wait_until='networkidle')
            HumanLikeBehavior.simulate_reading(self.page, 2, 4)
            
            # Check for CAPTCHA
            if self.page.locator('iframe[title*="captcha"]').count() > 0:
                logger.warning("CAPTCHA detected. Cannot apply.")
                return False
            
            # Find and click Easy Apply button
            easy_apply_button = self.page.locator('button[data-control-name="jobdetails_topcard_inapply"]')
            if easy_apply_button.count() == 0:
                logger.error("Easy Apply button not found")
                return False
            
            HumanLikeBehavior.human_click(self.page, 'button[data-control-name="jobdetails_topcard_inapply"]', wait_after=True)
            time.sleep(random.uniform(2, 3))
            
            # Process application form
            success = self._fill_application_form(require_approval)
            
            return success
            
        except Exception as e:
            logger.error(f"Error applying to job: {e}")
            return False
    
    def _fill_application_form(self, require_approval: bool) -> bool:
        """Fill out the Easy Apply form"""
        try:
            # Wait for form to load
            self.page.wait_for_selector('.jobs-easy-apply-modal', timeout=10000)
            time.sleep(random.uniform(1, 2))
            
            # Fill out form fields
            fields_filled = self._fill_fields()
            
            # Upload resume if needed
            resume_uploaded = self._upload_resume()
            
            # Answer questions if any
            questions_answered = self._answer_questions()
            
            # Review before submission
            if require_approval:
                logger.info("Application form filled. Waiting for approval...")
                input("Press Enter to submit the application (or Ctrl+C to cancel)...")
            
            # Submit application
            submit_button = self.page.locator('button[aria-label="Submit application"]')
            if submit_button.count() == 0:
                submit_button = self.page.locator('button:has-text("Submit")')
            
            if submit_button.count() > 0:
                HumanLikeBehavior.human_click(self.page, 'button[aria-label="Submit application"]', wait_after=False)
                time.sleep(random.uniform(2, 3))
                
                # Check for success
                success_indicator = self.page.locator('.jobs-s-apply__application-link')
                if success_indicator.count() > 0:
                    logger.info("Application submitted successfully")
                    return True
            
            logger.error("Could not submit application")
            return False
            
        except Exception as e:
            logger.error(f"Error filling application form: {e}")
            return False
    
    def _fill_fields(self) -> int:
        """Fill out form fields"""
        filled = 0
        
        try:
            # Phone number
            phone_input = self.page.locator('input[id*="phone"]')
            if phone_input.count() > 0 and not phone_input.input_value():
                phone_input.fill(self.resume_data.get('phone', ''))
                filled += 1
                HumanLikeBehavior.random_delay(0.5, 1)
            
            # Location/City
            city_input = self.page.locator('input[id*="city"]')
            if city_input.count() > 0 and not city_input.input_value():
                city_input.fill(self.resume_data.get('city', ''))
                filled += 1
                HumanLikeBehavior.random_delay(0.5, 1)
            
            # Additional fields as needed
            # LinkedIn forms vary, so this is a basic implementation
            
        except Exception as e:
            logger.debug(f"Error filling fields: {e}")
        
        return filled
    
    def _upload_resume(self) -> bool:
        """Upload resume file"""
        try:
            # Look for file input
            file_input = self.page.locator('input[type="file"]')
            if file_input.count() > 0:
                resume_path = self.resume_data.get('resume_path')
                if resume_path:
                    file_input.set_input_files(resume_path)
                    HumanLikeBehavior.random_delay(1, 2)
                    logger.info("Resume uploaded")
                    return True
        
        except Exception as e:
            logger.debug(f"Error uploading resume: {e}")
        
        return False
    
    def _answer_questions(self) -> int:
        """Answer application questions"""
        answered = 0
        
        try:
            # Look for question fields (this is simplified - real forms vary)
            # Radio buttons
            radio_groups = self.page.locator('fieldset').all()
            for group in radio_groups:
                # Try to select first option (or use resume data to answer intelligently)
                first_option = group.locator('input[type="radio"]').first
                if first_option.count() > 0:
                    first_option.click()
                    answered += 1
                    HumanLikeBehavior.random_delay(0.5, 1)
            
            # Text questions
            text_questions = self.page.locator('textarea, input[type="text"]:not([id*="phone"]):not([id*="city"])')
            # This would need more sophisticated logic based on question text
        
        except Exception as e:
            logger.debug(f"Error answering questions: {e}")
        
        return answered

