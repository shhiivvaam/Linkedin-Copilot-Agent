"""
Message Sender - Send messages via LinkedIn
"""

import time
import random
from typing import Dict, Any, Optional
from playwright.sync_api import Page
from loguru import logger

from browser_automation.human_like import HumanLikeBehavior


class MessageSender:
    """Send messages to recruiters on LinkedIn"""
    
    def __init__(self, page: Page, config: Dict[str, Any]):
        self.page = page
        self.config = config
    
    def send_message(self, recruiter_url: str, message: str, 
                    require_approval: bool = True) -> bool:
        """Send a message to a recruiter"""
        logger.info(f"Sending message to: {recruiter_url}")
        
        try:
            # Navigate to recruiter profile
            self.page.goto(recruiter_url, wait_until='networkidle')
            HumanLikeBehavior.simulate_reading(self.page, 1, 2)
            
            # Check for CAPTCHA
            if self.page.locator('iframe[title*="captcha"]').count() > 0:
                logger.warning("CAPTCHA detected. Cannot send message.")
                return False
            
            # Find and click "Message" button
            message_button = self.page.locator('button:has-text("Message")')
            if message_button.count() == 0:
                # Try alternative selectors
                message_button = self.page.locator('a[href*="/messaging/compose"]')
            
            if message_button.count() == 0:
                logger.error("Could not find Message button")
                return False
            
            HumanLikeBehavior.human_click(self.page, 'button:has-text("Message")', wait_after=True)
            time.sleep(random.uniform(1, 2))
            
            # Wait for message box to appear
            message_box = self.page.locator('.msg-form__contenteditable')
            if message_box.count() == 0:
                # Try alternative selector
                message_box = self.page.locator('[role="textbox"]')
            
            if message_box.count() == 0:
                logger.error("Could not find message input box")
                return False
            
            # Type message
            HumanLikeBehavior.human_type(
                self.page,
                '.msg-form__contenteditable',
                message
            )
            
            time.sleep(random.uniform(1, 2))
            
            # If approval required, pause here
            if require_approval:
                logger.info("Message ready to send. Waiting for approval...")
                input("Press Enter to send the message (or Ctrl+C to cancel)...")
            
            # Send message
            send_button = self.page.locator('button[aria-label="Send"]')
            if send_button.count() == 0:
                send_button = self.page.locator('button:has-text("Send")')
            
            if send_button.count() > 0:
                HumanLikeBehavior.human_click(self.page, 'button[aria-label="Send"]', wait_after=False)
                time.sleep(random.uniform(2, 3))
                logger.info("Message sent successfully")
                return True
            else:
                logger.error("Could not find Send button")
                return False
            
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

