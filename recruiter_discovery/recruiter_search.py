"""
Recruiter Search - Find Technical Recruiters on LinkedIn
"""

import time
import random
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page
from loguru import logger

from browser_automation.human_like import HumanLikeBehavior


class RecruiterSearch:
    """Search for Technical Recruiters on LinkedIn"""
    
    def __init__(self, page: Page, config: Dict[str, Any]):
        self.page = page
        self.config = config
        self.search_config = config.get('recruiter_discovery', {})
    
    def search(self, keywords: Optional[List[str]] = None, 
               location: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search for recruiters"""
        keywords = keywords or self.search_config.get('search_keywords', ['Technical Recruiter'])
        location = location or self.search_config.get('locations', ['United States'])[0]
        
        logger.info(f"Searching for recruiters: {keywords} in {location}")
        
        all_recruiters = []
        
        for keyword in keywords:
            recruiters = self._search_keyword(keyword, location)
            all_recruiters.extend(recruiters)
            time.sleep(random.uniform(2, 4))
        
        # Remove duplicates
        seen_urls = set()
        unique_recruiters = []
        for recruiter in all_recruiters:
            if recruiter['url'] not in seen_urls:
                seen_urls.add(recruiter['url'])
                unique_recruiters.append(recruiter)
        
        logger.info(f"Found {len(unique_recruiters)} unique recruiters")
        return unique_recruiters
    
    def _search_keyword(self, keyword: str, location: str) -> List[Dict[str, Any]]:
        """Search for a specific keyword"""
        # Navigate to LinkedIn People search
        search_url = f"https://www.linkedin.com/search/results/people/?keywords={keyword}&geoUrn=%5B%22103644278%22%5D"
        self.page.goto(search_url, wait_until='networkidle')
        time.sleep(random.uniform(2, 4))
        
        # Check for CAPTCHA
        if self.page.locator('iframe[title*="captcha"]').count() > 0:
            logger.warning("CAPTCHA detected. Manual intervention required.")
            return []
        
        recruiters = []
        max_results = self.search_config.get('max_results_per_search', 50)
        max_pages = 5
        
        for page_num in range(max_pages):
            # Extract recruiter profiles from current page
            page_recruiters = self._extract_recruiters_from_page()
            recruiters.extend(page_recruiters)
            
            logger.info(f"Page {page_num + 1}: Found {len(page_recruiters)} recruiters")
            
            if len(recruiters) >= max_results:
                break
            
            # Try to go to next page
            if not self._go_to_next_page():
                break
            
            HumanLikeBehavior.random_delay(2, 4)
        
        return recruiters[:max_results]
    
    def _extract_recruiters_from_page(self) -> List[Dict[str, Any]]:
        """Extract recruiter information from current page"""
        recruiters = []
        
        try:
            # Wait for search results
            self.page.wait_for_selector('.reusable-search__result-container', timeout=10000)
            HumanLikeBehavior.random_scroll(self.page)
            
            # Find all recruiter cards
            recruiter_cards = self.page.locator('.reusable-search__result-container')
            count = recruiter_cards.count()
            
            for i in range(min(count, 10)):  # Limit per page
                try:
                    card = recruiter_cards.nth(i)
                    
                    # Extract name
                    name_elem = card.locator('.entity-result__title-text a')
                    if name_elem.count() == 0:
                        continue
                    
                    name = name_elem.inner_text().strip()
                    url = name_elem.get_attribute('href')
                    if url and not url.startswith('http'):
                        url = f"https://www.linkedin.com{url}"
                    
                    # Extract title
                    title_elem = card.locator('.entity-result__primary-subtitle')
                    title = title_elem.inner_text().strip() if title_elem.count() > 0 else ""
                    
                    # Extract company
                    company_elem = card.locator('.entity-result__secondary-subtitle')
                    company = company_elem.inner_text().strip() if company_elem.count() > 0 else ""
                    
                    # Extract location
                    location_elem = card.locator('.entity-result__tertiary-subtitle')
                    location = location_elem.inner_text().strip() if location_elem.count() > 0 else ""
                    
                    recruiter = {
                        'name': name,
                        'url': url,
                        'title': title,
                        'company': company,
                        'location': location,
                        'relevance_score': 0,  # Will be calculated by ranker
                    }
                    
                    recruiters.append(recruiter)
                    
                except Exception as e:
                    logger.debug(f"Error extracting recruiter {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting recruiters from page: {e}")
        
        return recruiters
    
    def _go_to_next_page(self) -> bool:
        """Navigate to next page of results"""
        try:
            next_button = self.page.locator('button[aria-label="Next"]')
            if next_button.count() > 0 and next_button.is_enabled():
                HumanLikeBehavior.human_click(self.page, 'button[aria-label="Next"]')
                time.sleep(random.uniform(2, 4))
                return True
        except Exception:
            pass
        
        return False
    
    def get_recruiter_profile_details(self, recruiter_url: str) -> Dict[str, Any]:
        """Get detailed information from recruiter profile"""
        logger.info(f"Fetching profile details: {recruiter_url}")
        
        try:
            self.page.goto(recruiter_url, wait_until='networkidle')
            HumanLikeBehavior.simulate_reading(self.page, 2, 4)
            
            # Extract profile information
            profile = {
                'url': recruiter_url,
                'name': '',
                'headline': '',
                'company': '',
                'location': '',
                'about': '',
                'experience': [],
                'skills': [],
                'recent_activity': False,
            }
            
            # Name
            name_elem = self.page.locator('h1.text-heading-xlarge')
            if name_elem.count() > 0:
                profile['name'] = name_elem.inner_text().strip()
            
            # Headline
            headline_elem = self.page.locator('.text-body-medium.break-words')
            if headline_elem.count() > 0:
                profile['headline'] = headline_elem.first.inner_text().strip()
            
            # About section
            about_elem = self.page.locator('#about ~ .pvs-list__outer-container .inline-show-more-text')
            if about_elem.count() > 0:
                profile['about'] = about_elem.inner_text().strip()
            
            # Experience
            exp_section = self.page.locator('#experience ~ .pvs-list__outer-container')
            if exp_section.count() > 0:
                exp_items = exp_section.locator('.pvs-list__paged-list-item')
                for i in range(min(exp_items.count(), 5)):
                    exp_text = exp_items.nth(i).inner_text()
                    profile['experience'].append(exp_text)
            
            return profile
            
        except Exception as e:
            logger.error(f"Error fetching recruiter profile: {e}")
            return {'url': recruiter_url, 'error': str(e)}

