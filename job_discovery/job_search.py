"""
Job Search - Find relevant jobs on LinkedIn
"""

import time
import random
from typing import List, Dict, Any, Optional
from playwright.sync_api import Page
from loguru import logger

from browser_automation.human_like import HumanLikeBehavior


class JobSearch:
    """Search for jobs on LinkedIn"""
    
    def __init__(self, page: Page, config: Dict[str, Any]):
        self.page = page
        self.config = config
        self.search_config = config.get('job_discovery', {})
    
    def search(self, keywords: Optional[List[str]] = None,
              location: Optional[str] = None,
              easy_apply_only: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Search for jobs"""
        keywords = keywords or self.search_config.get('keywords', ['Software Engineer'])
        location = location or self.search_config.get('locations', ['San Francisco, CA'])[0]
        easy_apply_only = easy_apply_only if easy_apply_only is not None else self.search_config.get('easy_apply_only', True)
        
        logger.info(f"Searching for jobs: {keywords} in {location}")
        
        all_jobs = []
        
        for keyword in keywords:
            jobs = self._search_keyword(keyword, location, easy_apply_only)
            all_jobs.extend(jobs)
            time.sleep(random.uniform(2, 4))
        
        # Remove duplicates
        seen_urls = set()
        unique_jobs = []
        for job in all_jobs:
            if job['url'] not in seen_urls:
                seen_urls.add(job['url'])
                unique_jobs.append(job)
        
        logger.info(f"Found {len(unique_jobs)} unique jobs")
        return unique_jobs
    
    def _search_keyword(self, keyword: str, location: str, 
                       easy_apply_only: bool) -> List[Dict[str, Any]]:
        """Search for a specific keyword"""
        # Build search URL
        keyword_encoded = keyword.replace(' ', '%20')
        location_encoded = location.replace(' ', '%20').replace(',', '%2C')
        
        base_url = f"https://www.linkedin.com/jobs/search/?keywords={keyword_encoded}&location={location_encoded}"
        
        if easy_apply_only:
            base_url += "&f_EA=true"  # Easy Apply filter
        
        self.page.goto(base_url, wait_until='networkidle')
        time.sleep(random.uniform(2, 4))
        
        # Check for CAPTCHA
        if self.page.locator('iframe[title*="captcha"]').count() > 0:
            logger.warning("CAPTCHA detected. Manual intervention required.")
            return []
        
        jobs = []
        max_results = self.search_config.get('max_results_per_search', 100)
        max_pages = 10
        
        for page_num in range(max_pages):
            # Extract jobs from current page
            page_jobs = self._extract_jobs_from_page()
            jobs.extend(page_jobs)
            
            logger.info(f"Page {page_num + 1}: Found {len(page_jobs)} jobs")
            
            if len(jobs) >= max_results:
                break
            
            # Try to go to next page
            if not self._go_to_next_page():
                break
            
            HumanLikeBehavior.random_delay(2, 4)
        
        return jobs[:max_results]
    
    def _extract_jobs_from_page(self) -> List[Dict[str, Any]]:
        """Extract job information from current page"""
        jobs = []
        
        try:
            # Wait for job listings
            self.page.wait_for_selector('.jobs-search-results-list', timeout=10000)
            HumanLikeBehavior.random_scroll(self.page)
            
            # Find all job cards
            job_cards = self.page.locator('.job-search-card')
            count = job_cards.count()
            
            for i in range(min(count, 25)):  # Limit per page
                try:
                    card = job_cards.nth(i)
                    
                    # Extract job title
                    title_elem = card.locator('.base-search-card__title a')
                    if title_elem.count() == 0:
                        continue
                    
                    title = title_elem.inner_text().strip()
                    url = title_elem.get_attribute('href')
                    if url and not url.startswith('http'):
                        url = f"https://www.linkedin.com{url}"
                    
                    # Extract company
                    company_elem = card.locator('.base-search-card__subtitle a')
                    company = company_elem.inner_text().strip() if company_elem.count() > 0 else ""
                    
                    # Extract location
                    location_elem = card.locator('.job-search-card__location')
                    location = location_elem.inner_text().strip() if location_elem.count() > 0 else ""
                    
                    # Check for Easy Apply
                    easy_apply_elem = card.locator('.job-search-card__apply-button')
                    is_easy_apply = easy_apply_elem.count() > 0
                    
                    job = {
                        'title': title,
                        'url': url,
                        'company': company,
                        'location': location,
                        'easy_apply': is_easy_apply,
                        'description': '',  # Will be fetched separately if needed
                    }
                    
                    jobs.append(job)
                    
                except Exception as e:
                    logger.debug(f"Error extracting job {i}: {e}")
                    continue
            
        except Exception as e:
            logger.error(f"Error extracting jobs from page: {e}")
        
        return jobs
    
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
    
    def get_job_details(self, job_url: str) -> Dict[str, Any]:
        """Get detailed job description"""
        logger.info(f"Fetching job details: {job_url}")
        
        try:
            self.page.goto(job_url, wait_until='networkidle')
            HumanLikeBehavior.simulate_reading(self.page, 2, 4)
            
            job_details = {
                'url': job_url,
                'title': '',
                'company': '',
                'location': '',
                'description': '',
                'requirements': [],
                'easy_apply': False,
            }
            
            # Title
            title_elem = self.page.locator('.jobs-details-top-card__job-title')
            if title_elem.count() > 0:
                job_details['title'] = title_elem.inner_text().strip()
            
            # Company
            company_elem = self.page.locator('.jobs-details-top-card__company-name a')
            if company_elem.count() > 0:
                job_details['company'] = company_elem.inner_text().strip()
            
            # Location
            location_elem = self.page.locator('.jobs-details-top-card__bullet')
            if location_elem.count() > 0:
                job_details['location'] = location_elem.first.inner_text().strip()
            
            # Description
            desc_elem = self.page.locator('.jobs-description__content')
            if desc_elem.count() > 0:
                job_details['description'] = desc_elem.inner_text().strip()
            
            # Easy Apply button
            easy_apply_elem = self.page.locator('button[data-control-name="jobdetails_topcard_inapply"]')
            job_details['easy_apply'] = easy_apply_elem.count() > 0
            
            return job_details
            
        except Exception as e:
            logger.error(f"Error fetching job details: {e}")
            return {'url': job_url, 'error': str(e)}

