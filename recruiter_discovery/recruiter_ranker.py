"""
Recruiter Ranker - Rank recruiters by relevance
"""

from typing import List, Dict, Any
from datetime import datetime, timedelta
from loguru import logger


class RecruiterRanker:
    """Rank recruiters by relevance and activity"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.ranking_factors = config.get('recruiter_discovery', {}).get(
            'ranking_factors', 
            ['recent_activity', 'company_relevance', 'mutual_connections', 'profile_completeness']
        )
        self.min_activity_days = config.get('recruiter_discovery', {}).get('min_activity_days', 7)
    
    def rank(self, recruiters: List[Dict[str, Any]], 
             user_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Rank recruiters by relevance"""
        logger.info(f"Ranking {len(recruiters)} recruiters")
        
        for recruiter in recruiters:
            score = self._calculate_relevance_score(recruiter, user_profile)
            recruiter['relevance_score'] = score
        
        # Sort by relevance score (descending)
        ranked = sorted(recruiters, key=lambda x: x['relevance_score'], reverse=True)
        
        logger.info(f"Ranked recruiters. Top score: {ranked[0]['relevance_score']:.2f}" if ranked else "No recruiters to rank")
        return ranked
    
    def _calculate_relevance_score(self, recruiter: Dict[str, Any], 
                                   user_profile: Dict[str, Any]) -> float:
        """Calculate relevance score for a recruiter"""
        score = 0.0
        
        # Recent activity (0-30 points)
        if 'recent_activity' in self.ranking_factors:
            activity_score = self._score_recent_activity(recruiter)
            score += activity_score
        
        # Company relevance (0-25 points)
        if 'company_relevance' in self.ranking_factors:
            company_score = self._score_company_relevance(recruiter, user_profile)
            score += company_score
        
        # Profile completeness (0-20 points)
        if 'profile_completeness' in self.ranking_factors:
            completeness_score = self._score_profile_completeness(recruiter)
            score += completeness_score
        
        # Title relevance (0-25 points)
        title_score = self._score_title_relevance(recruiter)
        score += title_score
        
        return score
    
    def _score_recent_activity(self, recruiter: Dict[str, Any]) -> float:
        """Score based on recent activity"""
        # This would ideally check LinkedIn activity, but for now we'll use heuristics
        # If recruiter has detailed profile, assume recent activity
        if recruiter.get('about') or len(recruiter.get('experience', [])) > 0:
            return 20.0
        
        return 10.0
    
    def _score_company_relevance(self, recruiter: Dict[str, Any], 
                                  user_profile: Dict[str, Any]) -> float:
        """Score based on company relevance"""
        company = recruiter.get('company', '').lower()
        if not company:
            return 0.0
        
        # Check if company matches user's target companies or industry
        # This is a simplified version - could be enhanced with company database
        user_skills = [s.lower() for s in user_profile.get('skills', [])]
        
        # Tech companies get higher scores
        tech_keywords = ['tech', 'software', 'engineering', 'ai', 'cloud', 'saas']
        if any(keyword in company for keyword in tech_keywords):
            return 20.0
        
        return 10.0
    
    def _score_profile_completeness(self, recruiter: Dict[str, Any]) -> float:
        """Score based on profile completeness"""
        score = 0.0
        
        if recruiter.get('name'):
            score += 2.0
        if recruiter.get('title'):
            score += 3.0
        if recruiter.get('company'):
            score += 3.0
        if recruiter.get('location'):
            score += 2.0
        if recruiter.get('about'):
            score += 5.0
        if recruiter.get('experience'):
            score += 5.0
        
        return min(score, 20.0)
    
    def _score_title_relevance(self, recruiter: Dict[str, Any]) -> float:
        """Score based on title relevance"""
        title = recruiter.get('title', '').lower()
        if not title:
            return 0.0
        
        # High relevance keywords
        high_relevance = ['technical recruiter', 'engineering recruiter', 
                         'talent acquisition', 'tech recruiter', 'software recruiter']
        if any(keyword in title for keyword in high_relevance):
            return 25.0
        
        # Medium relevance
        medium_relevance = ['recruiter', 'talent', 'hiring', 'sourcing']
        if any(keyword in title for keyword in medium_relevance):
            return 15.0
        
        return 5.0

