"""
Message Generator - Creates personalized messages
"""

import os
from typing import Dict, Any, Optional
from loguru import logger


class MessageGenerator:
    """Generate personalized messages for recruiters"""
    
    def __init__(self, config: Dict[str, Any], user_profile: Dict[str, Any]):
        self.config = config
        self.user_profile = user_profile
        self.messaging_config = config.get('messaging', {})
        self.ai_config = config.get('ai', {})
        
        # Initialize AI client if configured
        self.ai_client = None
        if self.ai_config.get('provider') == 'openai':
            try:
                import openai
                api_key = os.getenv('OPENAI_API_KEY') or self.ai_config.get('api_key')
                if api_key:
                    self.ai_client = openai.OpenAI(api_key=api_key)
            except ImportError:
                logger.warning("OpenAI library not installed. Using template-based generation.")
    
    def generate_message(self, recruiter: Dict[str, Any], 
                        job_context: Optional[Dict[str, Any]] = None) -> str:
        """Generate a personalized message"""
        personalization_level = self.messaging_config.get('personalization_level', 'high')
        
        if personalization_level == 'high' and self.ai_client:
            return self._generate_ai_message(recruiter, job_context)
        else:
            return self._generate_template_message(recruiter, job_context)
    
    def _generate_ai_message(self, recruiter: Dict[str, Any], 
                            job_context: Optional[Dict[str, Any]]) -> str:
        """Generate message using AI"""
        try:
            prompt = self._build_prompt(recruiter, job_context)
            
            response = self.ai_client.chat.completions.create(
                model=self.ai_config.get('model', 'gpt-4-turbo-preview'),
                messages=[
                    {
                        'role': 'system',
                        'content': 'You are a professional job seeker writing a personalized LinkedIn message to a recruiter. Keep it concise (2-3 paragraphs), professional, and authentic. Do not sound like spam or a template.'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                temperature=self.ai_config.get('temperature', 0.7),
                max_tokens=self.ai_config.get('max_tokens', 500),
            )
            
            message = response.choices[0].message.content.strip()
            logger.info("Generated AI message")
            return message
            
        except Exception as e:
            logger.error(f"AI message generation failed: {e}. Falling back to template.")
            return self._generate_template_message(recruiter, job_context)
    
    def _build_prompt(self, recruiter: Dict[str, Any], 
                     job_context: Optional[Dict[str, Any]]) -> str:
        """Build prompt for AI generation"""
        prompt = f"""Write a personalized LinkedIn message to {recruiter.get('name', 'a recruiter')} at {recruiter.get('company', 'their company')}.

Recruiter Information:
- Name: {recruiter.get('name', 'N/A')}
- Title: {recruiter.get('title', 'N/A')}
- Company: {recruiter.get('company', 'N/A')}
- Headline: {recruiter.get('headline', 'N/A')}

My Profile:
- Name: {self.user_profile.get('name', 'N/A')}
- Title: {self.user_profile.get('title', 'N/A')}
- Skills: {', '.join(self.user_profile.get('skills', []))}
- Experience: {self.user_profile.get('experience_years', 0)} years

"""
        
        if job_context:
            prompt += f"""
Job Context:
- Title: {job_context.get('title', 'N/A')}
- Company: {job_context.get('company', 'N/A')}
"""
        
        prompt += """
Requirements:
- Keep it to 2-3 short paragraphs
- Be professional but friendly
- Reference something specific about their profile or company
- Mention your relevant skills briefly
- Ask permission to share your resume (don't attach it)
- Don't sound like spam or a mass message
"""
        
        return prompt
    
    def _generate_template_message(self, recruiter: Dict[str, Any], 
                                  job_context: Optional[Dict[str, Any]]) -> str:
        """Generate message using templates"""
        tone = self.messaging_config.get('tone', 'professional')
        
        # Greeting
        greeting = f"Hi {recruiter.get('name', 'there')},"
        
        # Opening
        if job_context:
            opening = f"I came across the {job_context.get('title', 'position')} at {job_context.get('company', 'your company')} and noticed your role in talent acquisition."
        else:
            opening = f"I noticed your work as a {recruiter.get('title', 'recruiter')} at {recruiter.get('company', 'your company')}."
        
        # Body
        skills_mention = ', '.join(self.user_profile.get('skills', [])[:3])
        body = f"I'm a {self.user_profile.get('title', 'professional')} with {self.user_profile.get('experience_years', 0)} years of experience in {skills_mention}. I'm currently exploring new opportunities and would love to connect."
        
        # Closing
        if self.messaging_config.get('include_resume_request', True):
            closing = "Would it be okay if I shared my resume with you? I'd appreciate any insights you might have on roles that could be a good fit."
        else:
            closing = "I'd appreciate any insights you might have on roles that could be a good fit."
        
        signoff = "Thanks for your time!"
        name = self.user_profile.get('name', '')
        
        message = f"{greeting}\n\n{opening}\n\n{body}\n\n{closing}\n\n{signoff}\n\n{name}"
        
        return message
    
    def validate_message(self, message: str) -> tuple:
        """Validate message quality"""
        # Check length
        if len(message) < 100:
            return False, "Message too short"
        
        if len(message) > 2000:
            return False, "Message too long"
        
        # Check for spam indicators
        spam_phrases = ['click here', 'limited time', 'act now', 'guaranteed']
        message_lower = message.lower()
        if any(phrase in message_lower for phrase in spam_phrases):
            return False, "Message contains spam-like phrases"
        
        return True, None

