"""
Human-like behavior simulation for browser automation
"""

import random
import time
from typing import Optional
from playwright.sync_api import Page, Locator
from loguru import logger


class HumanLikeBehavior:
    """Simulates human-like interactions"""
    
    @staticmethod
    def random_delay(min_seconds: float = 0.5, max_seconds: float = 2.0):
        """Random delay between actions"""
        delay = random.uniform(min_seconds, max_seconds)
        time.sleep(delay)
    
    @staticmethod
    def human_type(page: Page, selector: str, text: str, delay_range: tuple = (0.05, 0.15)):
        """Type text with human-like delays between keystrokes"""
        element = page.locator(selector)
        element.click()
        HumanLikeBehavior.random_delay(0.2, 0.5)
        
        for char in text:
            element.type(char, delay=random.uniform(*delay_range))
            # Occasional longer pauses (like thinking)
            if random.random() < 0.1:
                time.sleep(random.uniform(0.3, 0.8))
    
    @staticmethod
    def human_scroll(page: Page, direction: str = 'down', distance: Optional[int] = None):
        """Scroll with human-like behavior"""
        viewport_height = page.viewport_size['height']
        scroll_distance = distance or random.randint(300, viewport_height // 2)
        
        if direction == 'down':
            page.mouse.wheel(0, scroll_distance)
        else:
            page.mouse.wheel(0, -scroll_distance)
        
        # Random pause after scroll
        HumanLikeBehavior.random_delay(0.5, 1.5)
    
    @staticmethod
    def random_scroll(page: Page):
        """Random scrolling to simulate reading"""
        scrolls = random.randint(1, 3)
        for _ in range(scrolls):
            HumanLikeBehavior.human_scroll(page, direction=random.choice(['down', 'up']))
            HumanLikeBehavior.random_delay(1, 3)
    
    @staticmethod
    def human_click(page: Page, selector: str, wait_after: bool = True):
        """Click with human-like behavior"""
        element = page.locator(selector)
        
        # Move mouse to element first
        box = element.bounding_box()
        if box:
            # Random offset within element
            x = box['x'] + random.uniform(box['width'] * 0.2, box['width'] * 0.8)
            y = box['y'] + random.uniform(box['height'] * 0.2, box['height'] * 0.8)
            page.mouse.move(x, y)
            HumanLikeBehavior.random_delay(0.1, 0.3)
        
        element.click()
        
        if wait_after:
            HumanLikeBehavior.random_delay(0.5, 1.5)
    
    @staticmethod
    def simulate_reading(page: Page, min_seconds: float = 2.0, max_seconds: float = 5.0):
        """Simulate reading a page"""
        reading_time = random.uniform(min_seconds, max_seconds)
        
        # Occasional scrolling while reading
        scrolls = random.randint(0, 2)
        for _ in range(scrolls):
            time.sleep(reading_time / (scrolls + 1))
            HumanLikeBehavior.human_scroll(page)
        
        time.sleep(reading_time / (scrolls + 1))
    
    @staticmethod
    def wait_for_element(page: Page, selector: str, timeout: int = 30000) -> bool:
        """Wait for element with human-like delay"""
        try:
            page.wait_for_selector(selector, timeout=timeout)
            HumanLikeBehavior.random_delay(0.3, 0.8)
            return True
        except Exception:
            return False

