"""
Requirement Matcher - Match resume to job requirements
"""

from typing import Dict, Any, List
from loguru import logger


class RequirementMatcher:
    """Match resume data to job requirements"""
    
    def __init__(self, resume_data: Dict[str, Any]):
        self.resume_data = resume_data
    
    def calculate_match_score(self, job_description: str) -> float:
        """Calculate how well resume matches job requirements"""
        resume_skills = [s.lower() for s in self.resume_data.get('skills', [])]
        resume_text = self.resume_data.get('raw_text', '').lower()
        
        job_lower = job_description.lower()
        
        # Count skill matches
        skill_matches = sum(1 for skill in resume_skills if skill in job_lower)
        total_skills = len(resume_skills)
        skill_score = (skill_matches / total_skills * 100) if total_skills > 0 else 0
        
        # Check for common keywords
        common_keywords = [
            'python', 'javascript', 'react', 'aws', 'docker', 'kubernetes',
            'sql', 'api', 'rest', 'microservices', 'agile', 'scrum'
        ]
        keyword_matches = sum(1 for keyword in common_keywords if keyword in job_lower and keyword in resume_text)
        keyword_score = (keyword_matches / len(common_keywords) * 100)
        
        # Overall match score (weighted average)
        match_score = (skill_score * 0.7 + keyword_score * 0.3)
        
        return min(match_score, 100.0)
    
    def should_apply(self, job_description: str, min_match_score: float = 50.0) -> tuple[bool, float]:
        """Determine if should apply based on match score"""
        match_score = self.calculate_match_score(job_description)
        should_apply = match_score >= min_match_score
        
        return should_apply, match_score
    
    def generate_answers(self, questions: List[Dict[str, Any]]) -> Dict[str, str]:
        """Generate answers to application questions based on resume"""
        answers = {}
        
        for question in questions:
            question_text = question.get('text', '').lower()
            question_id = question.get('id', '')
            
            # Simple rule-based answering
            if 'years of experience' in question_text or 'experience' in question_text:
                years = self.resume_data.get('experience_years', 0)
                answers[question_id] = str(years)
            
            elif 'location' in question_text or 'relocate' in question_text:
                city = self.resume_data.get('city', '')
                answers[question_id] = city
            
            elif 'authorized' in question_text or 'work authorization' in question_text:
                answers[question_id] = 'Yes'  # Default - should be configured
            
            elif 'salary' in question_text or 'compensation' in question_text:
                answers[question_id] = ''  # Leave blank or use configured value
            
            else:
                # Try to match skills or experience
                resume_text = self.resume_data.get('raw_text', '').lower()
                if any(skill.lower() in question_text for skill in self.resume_data.get('skills', [])):
                    answers[question_id] = 'Yes'
                else:
                    answers[question_id] = ''  # Leave blank for manual review
        
        return answers

