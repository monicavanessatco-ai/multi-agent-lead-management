#!/usr/bin/env python3
"""
Agents package for Multi-Agent Lead Management System
"""

from .instagram_agent import InstagramAgent
from .webform_agent import WebFormAgent
from .followup_agent import FollowUpAgent

__all__ = ['InstagramAgent', 'WebFormAgent', 'FollowUpAgent']