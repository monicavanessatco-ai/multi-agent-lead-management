#!/usr/bin/env python3
"""
Web Form Agent - Handles web form submissions and qualification
Part of Multi-Agent Lead Management System
"""

import asyncio
import random
from datetime import datetime
from typing import Dict, List
from main import BaseAgent, Lead

class WebFormAgent(BaseAgent):
    """Handles web form submissions and qualification"""
    
    def __init__(self, config: Dict):
        super().__init__("WebForm", config)
        self.typeform_webhook_url = config.get("typeform_webhook")
        self.calendar_links = {
            "high": "https://calendly.com/senior-closer",
            "medium": "https://calendly.com/sales-specialist", 
            "low": "https://calendly.com/junior-setter"
        }
    
    async def continuous_monitor(self):
        """Monitor for new web form submissions"""
        self.logger.info("Starting web form monitoring loop...")
        
        while self.is_running:
            try:
                # Check for new form submissions
                new_submissions = await self.check_typeform_submissions()
                
                for submission in new_submissions:
                    lead = await self.process_form_submission(submission)
                    if lead:
                        await self.route_lead_by_qualification(lead)
                        await self.send_to_orchestrator(lead)
                
                # Check every minute for form submissions
                await asyncio.sleep(60)
                
            except Exception as e:
                self.logger.error(f"Error in web form monitoring: {e}")
                await asyncio.sleep(120)
    
    async def check_typeform_submissions(self) -> List[Dict]:
        """Check for new form submissions (simulated)"""
        # In production, this would integrate with Typeform API
        
        if random.random() < 0.05:  # 5% chance of new submission per check
            sample_submissions = [
                {
                    "form_id": "lead_qualification_form",
                    "response_id": f"resp_{random.randint(10000, 99999)}",
                    "submitted_at": datetime.now(),
                    "answers": {
                        "name": random.choice([
                            "Sarah Johnson", "Mike Chen", "Emily Rodriguez", 
                            "David Kim", "Lisa Thompson", "James Wilson"
                        ]),
                        "email": f"user{random.randint(1, 1000)}@example.com",
                        "phone": f"+1555{random.randint(100, 999)}{random.randint(1000, 9999)}",
                        "company": random.choice([
                            "Tech Startup Inc", "Growth Solutions LLC", "Digital Marketing Pro",
                            "E-commerce Plus", "Consulting Experts", "Sales Acceleration Co"
                        ]),
                        "revenue": random.choice([
                            "$0-$50K", "$50K-$100K", "$100K-$500K", 
                            "$500K-$1M", "$1M-$5M", "$5M+"
                        ]),
                        "pain_points": random.choice([
                            "Need help scaling our sales team",
                            "Struggling to generate consistent leads",
                            "Want to improve our conversion rates", 
                            "Need better sales processes",
                            "Looking to hire and train sales people",
                            "Want to automate our sales funnel"
                        ]),
                        "timeline": random.choice([
                            "ASAP", "Within 30 days", "Within 3 months", 
                            "Within 6 months", "Not sure", "Just exploring"
                        ]),
                        "budget": random.choice([
                            "$1K-$5K", "$5K-$10K", "$10K-$25K", 
                            "$25K-$50K", "$50K+", "Not sure"
                        ])
                    }
                }
            ]
            return sample_submissions
        
        return []
    
    async def process_form_submission(self, submission: Dict) -> Lead:
        """Process form submission and calculate qualification score"""
        answers = submission["answers"]
        
        # Advanced qualification scoring algorithm
        score = self.calculate_advanced_qualification_score(answers)
        
        lead = Lead(
            id=f"web_{submission['response_id']}",
            name=answers.get("name", ""),
            email=answers.get("email", ""),
            phone=answers.get("phone", ""),
            source="webform",
            qualification_score=min(score, 10),
            status="new",
            created_at=submission["submitted_at"],
            notes=[
                f"Company: {answers.get('company', 'N/A')}", 
                f"Revenue: {answers.get('revenue', 'N/A')}",
                f"Pain points: {answers.get('pain_points', 'N/A')}",
                f"Timeline: {answers.get('timeline', 'N/A')}",
                f"Budget: {answers.get('budget', 'N/A')}"
            ]
        )
        
        self.logger.info(f"Processed web form lead: {lead.name} (Score: {score}/10)")
        return lead
    
    def calculate_advanced_qualification_score(self, answers: Dict) -> int:
        """Calculate sophisticated qualification score"""
        score = 5  # Base score
        
        # Revenue scoring (higher revenue = higher score)
        revenue = answers.get("revenue", "").lower()
        if "$5m" in revenue:
            score += 4
        elif "$1m" in revenue:
            score += 3
        elif "$500k" in revenue:
            score += 2
        elif "$100k" in revenue:
            score += 1
        elif "$50k" in revenue:
            score += 0
        else:  # Below $50K
            score -= 1
        
        # Timeline urgency scoring
        timeline = answers.get("timeline", "").lower()
        if "asap" in timeline or "immediately" in timeline:
            score += 3
        elif "30 days" in timeline or "month" in timeline:
            score += 2
        elif "3 months" in timeline:
            score += 1
        elif "6 months" in timeline:
            score += 0
        else:  # "not sure" or "exploring"
            score -= 1
        
        # Budget scoring
        budget = answers.get("budget", "").lower()
        if "$50k" in budget:
            score += 3
        elif "$25k" in budget:
            score += 2
        elif "$10k" in budget:
            score += 1
        elif "$5k" in budget:
            score += 0
        else:  # Lower budget or "not sure"
            score -= 1
        
        # Pain point intensity analysis
        pain_points = answers.get("pain_points", "").lower()
        urgent_keywords = ["struggling", "urgent", "critical", "failing", "desperate", "need help"]
        growth_keywords = ["scale", "grow", "expand", "increase", "improve"]
        
        for keyword in urgent_keywords:
            if keyword in pain_points:
                score += 1
        
        for keyword in growth_keywords:
            if keyword in pain_points:
                score += 1
        
        return max(1, score)  # Minimum score of 1
    
    async def route_lead_by_qualification(self, lead: Lead):
        """Route lead to appropriate calendar based on qualification"""
        if lead.qualification_score >= 8:
            priority = "high"
            calendar_link = self.calendar_links["high"]
            follow_up_delay = 2  # 2 hours for high-priority leads
        elif lead.qualification_score >= 6:
            priority = "medium"
            calendar_link = self.calendar_links["medium"]
            follow_up_delay = 6  # 6 hours for medium-priority leads
        else:
            priority = "low"
            calendar_link = self.calendar_links["low"]
            follow_up_delay = 24  # 24 hours for low-priority leads
        
        # Send immediate qualification email
        await self.send_qualification_email(lead, calendar_link, priority)
        
        # Schedule follow-up if they don't book
        await self.schedule_follow_up(lead, follow_up_delay)
    
    async def send_qualification_email(self, lead: Lead, calendar_link: str, priority: str):
        """Send personalized email based on qualification level"""
        
        if priority == "high":
            subject = f"Exclusive consultation opportunity for {lead.name}"
            email_body = f"""Hi {lead.name},

Thank you for your interest in our services. Based on your submission, you appear to be an excellent fit for our premium consultation program.

I'd like to personally invite you to schedule a strategy session with our senior consultant who has helped companies similar to yours achieve remarkable growth.

This exclusive consultation is valued at $500, but it's complimentary for qualified prospects like yourself.

Book your session here: {calendar_link}

Best regards,
The Growth Team"""
            
        elif priority == "medium":
            subject = f"Let's discuss your growth goals, {lead.name}"
            email_body = f"""Hi {lead.name},

Thanks for reaching out! I reviewed your submission and I believe we can definitely help you achieve your growth objectives.

I'd love to schedule a consultation to discuss your specific situation and share some strategies that have worked well for businesses in your position.

Schedule your consultation here: {calendar_link}

Looking forward to speaking with you,
The Sales Team"""
            
        else:  # low priority
            subject = f"Thanks for your interest, {lead.name}"
            email_body = f"""Hi {lead.name},

Thank you for your interest in our services. While we typically work with larger organizations, I'd still like to explore how we might be able to help.

Please feel free to schedule a brief consultation to discuss your needs:

{calendar_link}

Best regards,
The Team"""
        
        # In production, this would integrate with email service (SendGrid, etc.)
        self.logger.info(f"Sending {priority} priority email to {lead.email}")
        self.logger.info(f"Subject: {subject}")
    
    async def schedule_follow_up(self, lead: Lead, delay_hours: int):
        """Schedule follow-up sequence if lead doesn't book"""
        # In production, this would integrate with a job queue (Celery, etc.)
        follow_up_time = datetime.now().timestamp() + (delay_hours * 3600)
        
        self.logger.info(f"Scheduled follow-up for {lead.name} in {delay_hours} hours")
        
        # Send A2A message to FollowUp agent
        await self.send_a2a_message("FollowUp", {
            "message_type": "schedule_follow_up",
            "payload": {
                "lead": lead.to_dict(),
                "follow_up_time": follow_up_time,
                "sequence_type": "no_booking_follow_up"
            }
        })
    
    async def send_to_orchestrator(self, lead: Lead):
        """Send processed lead to orchestrator"""
        self.logger.info(f"Sending processed lead {lead.id} to orchestrator")
        
        await self.send_a2a_message("Orchestrator", {
            "message_type": "new_lead",
            "payload": lead.to_dict()
        })
    
    async def send_a2a_message(self, target_agent: str, message: Dict):
        """Send A2A protocol message to another agent"""
        a2a_message = {
            "from_agent": self.name,
            "to_agent": target_agent,
            "timestamp": datetime.now().isoformat(),
            **message
        }
        
        # In production, this would use ADK's A2A messaging
        self.logger.info(f"A2A Message to {target_agent}: {a2a_message}")
    
    def get_agent_metrics(self) -> Dict:
        """Return WebForm agent specific metrics"""
        return {
            "agent_name": self.name,
            "status": "running" if self.is_running else "stopped",
            "monitoring_frequency": "60 seconds",
            "qualification_algorithm": "advanced_scoring",
            "routing_calendars": len(self.calendar_links),
            "auto_follow_up": "enabled"
        }