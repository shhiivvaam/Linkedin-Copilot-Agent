"""
Browser Manager - Handles browser session and automation
"""

import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from playwright.sync_api import (
    sync_playwright,
    Page,
    Browser,
    BrowserContext,
    TimeoutError as PlaywrightTimeoutError,
)
from loguru import logger
import time
import random


class BrowserManager:
    """Manages browser automation with persistent sessions"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.cookies_file = config.get('linkedin', {}).get('cookies_file', './sessions/linkedin_cookies.json')
        self.session_dir = config.get('linkedin', {}).get('session_dir', './sessions')
        
        # Ensure session directory exists
        Path(self.session_dir).mkdir(parents=True, exist_ok=True)
    
    def start(self) -> Page:
        """Start browser and load LinkedIn session"""
        logger.info("Starting browser...")
        self.playwright = sync_playwright().start()
        
        browser_config = self.config.get('browser', {})
        
        self.browser = self.playwright.chromium.launch(
            headless=browser_config.get('headless', False),
            slow_mo=browser_config.get('slow_mo', 100),
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox',
            ]
        )
        
        viewport = {
            'width': browser_config.get('viewport_width', 1920),
            'height': browser_config.get('viewport_height', 1080),
        }
        
        self.context = self.browser.new_context(
            viewport=viewport,
            user_agent=browser_config.get('user_agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'),
            locale='en-US',
            timezone_id='America/Los_Angeles',
        )
        
        # Remove webdriver property
        self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        self.page = self.context.new_page()
        
        # Load cookies if they exist
        self._load_cookies()
        
        logger.info("Browser started successfully")
        return self.page
    
    def _load_cookies(self):
        """Load saved cookies from file"""
        if os.path.exists(self.cookies_file):
            try:
                with open(self.cookies_file, 'r') as f:
                    cookies = json.load(f)
                    self.context.add_cookies(cookies)
                    logger.info(f"Loaded {len(cookies)} cookies from session")
            except Exception as e:
                logger.warning(f"Failed to load cookies: {e}")
    
    def save_cookies(self):
        """Save current cookies to file"""
        try:
            cookies = self.context.cookies()
            with open(self.cookies_file, 'w') as f:
                json.dump(cookies, f, indent=2)
            logger.info(f"Saved {len(cookies)} cookies to session")
        except Exception as e:
            logger.error(f"Failed to save cookies: {e}")
    
    def login(self, email: str, password: str) -> bool:
        """Login to LinkedIn"""
        logger.info("Attempting LinkedIn login...")
        
        try:
            self.page.goto('https://www.linkedin.com/login', wait_until='networkidle')
            time.sleep(random.uniform(2, 4))
            
            # Fill email
            email_input = self.page.locator('input#username')
            email_input.fill(email)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Fill password
            password_input = self.page.locator('input#password')
            password_input.fill(password)
            time.sleep(random.uniform(0.5, 1.5))
            
            # Click login button
            login_button = self.page.locator('button[type="submit"]')
            login_button.click()

            try:
                # Wait for navigation to main feed
                self.page.wait_for_url('**/feed**', timeout=30000)
                time.sleep(random.uniform(2, 4))

                # Check for CAPTCHA or OTP even after successful navigation
                if self._check_captcha_or_otp():
                    logger.warning("CAPTCHA or OTP detected after login. Manual intervention required.")
                    return False

                # Save cookies after successful login
                self.save_cookies()
                logger.info("Login successful")
                return True

            except PlaywrightTimeoutError:
                # We timed out waiting for the feed - see if we hit a challenge page
                if self._check_captcha_or_otp():
                    logger.error("Login failed due to CAPTCHA/OTP challenge. Please complete it manually.")
                else:
                    logger.error("Login failed: timeout waiting for LinkedIn feed.")
                return False

        except Exception as e:
            logger.error(f"Login failed: {e}")
            return False
    
    def _check_captcha_or_otp(self) -> bool:
        """Check if CAPTCHA or OTP is present"""
        try:
            # Check for CAPTCHA
            captcha_selectors = [
                'iframe[title*="captcha"]',
                'div[id*="captcha"]',
                'div[class*="captcha"]',
            ]
            
            for selector in captcha_selectors:
                if self.page.locator(selector).count() > 0:
                    return True
            
            # Check for OTP/verification
            otp_selectors = [
                'input[id*="verification"]',
                'input[id*="otp"]',
                'div[class*="challenge"]',
                'div:has-text("verification")',
            ]
            
            for selector in otp_selectors:
                if self.page.locator(selector).count() > 0:
                    return True
            
            return False
            
        except Exception:
            return False
    
    def check_captcha_or_otp(self) -> bool:
        """Public method to check for CAPTCHA/OTP"""
        return self._check_captcha_or_otp()
    
    def navigate(self, url: str, wait_until: str = 'networkidle'):
        """Navigate to URL with human-like delay"""
        logger.debug(f"Navigating to: {url}")
        self.page.goto(url, wait_until=wait_until)
        time.sleep(random.uniform(1, 3))
        
        # Check for CAPTCHA/OTP
        if self._check_captcha_or_otp():
            logger.warning("CAPTCHA or OTP detected during navigation")
            raise Exception("CAPTCHA/OTP detected - manual intervention required")
    
    def close(self):
        """Close browser and save session"""
        logger.info("Closing browser...")
        
        if self.page:
            self.save_cookies()
        
        if self.context:
            self.context.close()
        
        if self.browser:
            self.browser.close()
        
        if self.playwright:
            self.playwright.stop()
        
        logger.info("Browser closed")

