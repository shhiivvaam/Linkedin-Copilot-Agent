"""
Resume Parser - Extract information from resume
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger


class ResumeParser:
    """Parse resume files and extract structured data"""
    
    def __init__(self, resume_path: str, user_profile: Dict[str, Any]):
        self.resume_path = resume_path
        self.user_profile = user_profile
        self.resume_data = {}
    
    def parse(self) -> Dict[str, Any]:
        """Parse resume file"""
        if not os.path.exists(self.resume_path):
            logger.warning(f"Resume file not found: {self.resume_path}")
            return self._get_default_data()
        
        file_ext = Path(self.resume_path).suffix.lower()
        
        if file_ext == '.pdf':
            return self._parse_pdf()
        elif file_ext in ['.docx', '.doc']:
            return self._parse_docx()
        else:
            logger.warning(f"Unsupported resume format: {file_ext}")
            return self._get_default_data()
    
    def _parse_pdf(self) -> Dict[str, Any]:
        """Parse PDF resume"""
        try:
            import PyPDF2
            
            with open(self.resume_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                return self._extract_data_from_text(text)
                
        except Exception as e:
            logger.error(f"Error parsing PDF: {e}")
            return self._get_default_data()
    
    def _parse_docx(self) -> Dict[str, Any]:
        """Parse DOCX resume"""
        try:
            from docx import Document
            
            doc = Document(self.resume_path)
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            return self._extract_data_from_text(text)
            
        except Exception as e:
            logger.error(f"Error parsing DOCX: {e}")
            return self._get_default_data()
    
    def _extract_data_from_text(self, text: str) -> Dict[str, Any]:
        """Extract structured data from resume text"""
        # This is a simplified parser - could be enhanced with NLP
        resume_data = {
            'name': self.user_profile.get('name', ''),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'city': self.user_profile.get('location', '').split(',')[0] if self.user_profile.get('location') else '',
            'skills': self.user_profile.get('skills', []),
            'experience_years': self.user_profile.get('experience_years', 0),
            'resume_path': self.resume_path,
            'raw_text': text,
        }
        
        return resume_data
    
    def _extract_email(self, text: str) -> str:
        """Extract email from text"""
        import re
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        matches = re.findall(email_pattern, text)
        return matches[0] if matches else ''
    
    def _extract_phone(self, text: str) -> str:
        """Extract phone number from text"""
        import re
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\d{3}-\d{3}-\d{4}',
        ]
        for pattern in phone_patterns:
            matches = re.findall(pattern, text)
            if matches:
                return matches[0]
        return ''
    
    def _get_default_data(self) -> Dict[str, Any]:
        """Get default resume data from user profile"""
        return {
            'name': self.user_profile.get('name', ''),
            'email': '',
            'phone': '',
            'city': self.user_profile.get('location', '').split(',')[0] if self.user_profile.get('location') else '',
            'skills': self.user_profile.get('skills', []),
            'experience_years': self.user_profile.get('experience_years', 0),
            'resume_path': self.resume_path,
            'raw_text': '',
        }

