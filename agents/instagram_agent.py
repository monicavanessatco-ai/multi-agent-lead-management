#!/usr/bin/env python3
"""
Instagram Agent - Handles Instagram DM monitoring and responses
Part of Multi-Agent Lead Management System
"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
from main import BaseAgent, Lead

class InstagramAgent(BaseAgent):
    """Handles Instagram DM monitoring and responses"""
    
    def __init__(self, config: Dict):
        super().__init__("Instagram", config)
        self.qualification_keywords = [
            "interested", "pricing", "schedule", "call", "demo", "learn more",
            "consultation", "help", "services", "book", "appointment"
        ]
        self.high_intent_keywords = [
            "ready to buy", "when can we start", "price", "cost", "budget",
            "asap", "urgent", "immediately", "today"
        ]
    
    async def continuous_monitor(self):
        """Continuous loop monitoring Instagram DMs"""
        self.logger.info("Starting Instagram DM monitoring loop...")
        
        while self.is_running:
            try:
                # Simulate checking Instagram API for new DMs
                new_messages = await self.check_instagram_messages()
                
                for message in new_messages:
                    lead = await self.process_instagram_message(message)
                    if lead:
                        await self.send_to_orchestrator(lead)
                
                # Check every 30 seconds for real-time responsiveness
                await asyncio.sleep(30)
                
            except Exception as e:
                self.logger.error(f"Error in Instagram monitoring: {e}")
                await asyncio.sleep(60)  # Longer delay on error
    
    async def check_instagram_messages(self) -> List[Dict]:
        """Simulate checking Instagram API for new DMs"""
        # In production, this would integrate with Instagram Graph API
        # For demo, simulate incoming messages
        
        import random
        
        if random.random() < 0.1:  # 10% chance of new message per check
            sample_messages = [
                {
                    "user_id": f"user_{random.randint(1000, 9999)}",
                    "username": f"potential_client_{random.randint(1, 100)}",
                    "message": random.choice([
                        "Hi, I'm interested in your services. Can we schedule a call?",
                        "What are your pricing options?",
                        "I need help with my business. When can we talk?",
                        "Saw your post, very interested in learning more",
                        "Can you help me scale my sales team?",
                        "Looking for consultation, when are you available?"
                    ]),
                    "timestamp": datetime.now()
                }
            ]
            return sample_messages
        
        return []
    
    async def process_instagram_message(self, message: Dict) -> Optional[Lead]:
        """Process incoming Instagram message and qualify lead"""
        text = message["message"].lower()
        
        # Calculate qualification score
        score = self.calculate_qualification_score(text)
        
        if score >= 4:  # Qualified lead threshold
            lead = Lead(
                id=f"ig_{message['user_id']}_{int(datetime.now().timestamp())}",
                name=message["username"],
                email="",  # Will be collected in follow-up
                phone="",  # Will be collected in follow-up
                source="instagram",
                qualification_score=min(score, 10),
                status="new",
                created_at=message["timestamp"],
                notes=[f"Initial message: {message['message']}"]
            )
            
            # Send immediate auto-response
            await self.send_auto_response(message["user_id"], score, message["username"])
            
            self.logger.info(f"Qualified Instagram lead: {lead.name} (Score: {score}/10)")
            return lead
        else:
            # Send polite response even for unqualified leads
            await self.send_polite_response(message["user_id"], message["username"])
        
        return None
    
    def calculate_qualification_score(self, text: str) -> int:
        """Calculate lead qualification score based on message content"""
        score = 0
        
        # Base scoring for qualification keywords
        for keyword in self.qualification_keywords:
            if keyword in text:
                score += 1
        
        # Higher scoring for high-intent keywords
        for keyword in self.high_intent_keywords:
            if keyword in text:
                score += 2
        
        # Question marks indicate engagement
        score += text.count('?')
        
        # Longer messages show more engagement
        if len(text) > 50:
            score += 1
        if len(text) > 100:
            score += 1
        
        # Business-related terms
        business_terms = ["business", "company", "revenue", "sales", "team", "growth"]
        for term in business_terms:
            if term in text:
                score += 1
        
        return score
    
    async def send_auto_response(self, user_id: str, qualification_score: int, username: str):
        """Send intelligent auto-response based on qualification score"""
        
        if qualification_score >= 8:
            response = f"Hi {username}! Thanks for reaching out. You sound like exactly the type of client we love working with. I'm going to have our senior consultant reach out within the next hour to get you scheduled. What's the best number to reach you at?"
            
        elif qualification_score >= 6:
            response = f"Hi {username}! Thanks for your interest. I'd love to learn more about your specific situation. Can you tell me a bit about your business and what challenges you're facing? This will help me connect you with the right person on our team."
            
        else:
            response = f"Hi {username}! Thanks for reaching out. I'd be happy to help you learn more about what we do. What specific area are you most interested in discussing?"
        
        # In production, this would call Instagram API to send DM
        self.logger.info(f"Auto-response sent to {user_id}: {response}")
    
    async def send_polite_response(self, user_id: str, username: str):
        """Send polite response to unqualified leads"""
        response = f"Hi {username}! Thanks for your message. I'll get back to you with some helpful information soon!"
        self.logger.info(f"Polite response sent to {user_id}: {response}")
    
    async def send_to_orchestrator(self, lead: Lead):
        """Send qualified lead to orchestrator using A2A protocol"""
        # In production, this would use ADK's A2A protocol for agent communication
        self.logger.info(f"Sending qualified lead {lead.id} to orchestrator via A2A protocol")
        
        # Simulate A2A message to orchestrator
        a2a_message = {
            "from_agent": self.name,
            "to_agent": "Orchestrator",
            "message_type": "new_lead",
            "payload": lead.to_dict(),
            "timestamp": datetime.now().isoformat()
        }
        
        # In real implementation, this would be sent via ADK's messaging system
        self.logger.info(f"A2A Message: {a2a_message}")
    
    async def handle_agent_communication(self, message: Dict):
        """Handle incoming A2A messages from other agents"""
        if message["message_type"] == "lead_update":
            lead_id = message["payload"]["lead_id"]
            new_status = message["payload"]["status"]
            self.logger.info(f"Received lead update via A2A: {lead_id} -> {new_status}")
        
        elif message["message_type"] == "follow_up_request":
            lead_data = message["payload"]
            await self.send_follow_up_dm(lead_data)
    
    async def send_follow_up_dm(self, lead_data: Dict):
        """Send follow-up DM as requested by FollowUp agent"""
        username = lead_data["name"]
        follow_up_message = f"Hi {username}! Just following up on our conversation. Did you have a chance to think about scheduling that consultation we discussed?"
        
        self.logger.info(f"Sending follow-up DM to {username}: {follow_up_message}")
    
    def get_agent_metrics(self) -> Dict:
        """Return Instagram agent specific metrics"""
        return {
            "agent_name": self.name,
            "status": "running" if self.is_running else "stopped",
            "monitoring_frequency": "30 seconds",
            "qualification_threshold": "4/10",
            "response_time": "< 30 seconds"
        }