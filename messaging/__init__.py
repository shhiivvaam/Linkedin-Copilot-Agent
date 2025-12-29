"""
Messaging System Module
Generates personalized outreach messages for recruiters
"""

from .message_generator import MessageGenerator
from .message_sender import MessageSender

__all__ = ['MessageGenerator', 'MessageSender']

