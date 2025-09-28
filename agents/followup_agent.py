#!/usr/bin/env python3
"""
Follow-up Agent - Handles automated follow-up sequences
Part of Multi-Agent Lead Management System
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List
from main import BaseAgent, Lead

class FollowUpAgent(BaseAgent):
    """Handles automated follow-up sequences"""
    
    def __init__(self, config: Dict):
        super().__init__("FollowUp", config)
        self.pending_follow_ups = []
        self.follow_up_sequences = {
            "no_response_24h": [
                {"delay_hours": 24, "channel": "email", "template": "follow_up_1"},
                {"delay_hours": 72, "channel": "sms", "template": "follow_up_2"},
                {"delay_hours": 168, "channel": "instagram", "template": "follow_up_3"}
            ],
            "form_no_schedule": [
                {"delay_hours": 2, "channel": "email", "template": "immediate_follow_up"},
                {"delay_hours": 24, "channel": "sms", "template": "reminder_to_schedule"},
                {"delay_hours": 72, "channel": "email", "template": "last_chance"}
            ],
            "instagram_no_response": [
                {"delay_hours": 6, "channel": "instagram", "template": "gentle_reminder"},
                {"delay_hours": 48, "channel": "email", "template": "value_proposition"},
                {"delay_hours": 120, "channel": "sms", "template": "final_outreach"}
            ]
        }
    
    async def continuous_monitor(self):
        """Continuously monitor leads needing follow-up"""
        self.logger.info("Starting follow-up monitoring loop...")
        
        while self.is_running:
            try:
                # Check for scheduled follow-ups that are due
                await self.process_due_follow_ups()
                
                # Check for leads that need follow-up sequences
                await self.identify_new_follow_up_candidates()
                
                # Check every 5 minutes for follow-up opportunities
                await asyncio.sleep(300)
                
            except Exception as e:
                self.logger.error(f"Error in follow-up monitoring: {e}")
                await asyncio.sleep(600)
    
    async def process_due_follow_ups(self):
        """Process follow-ups that are due to be sent"""
        current_time = datetime.now()
        due_follow_ups = []
        
        # Find follow-ups that are due
        for follow_up in self.pending_follow_ups:
            if follow_up["scheduled_time"] <= current_time:
                due_follow_ups.append(follow_up)
        
        # Process each due follow-up
        for follow_up in due_follow_ups:
            await self.execute_follow_up_step(follow_up)
            self.pending_follow_ups.remove(follow_up)
            
            # Schedule next step in sequence if applicable
            await self.schedule_next_follow_up_step(follow_up)
    
    async def identify_new_follow_up_candidates(self):
        """Identify leads that need new follow-up sequences"""
        # This would typically query a database for leads meeting certain criteria
        # For demo purposes, we'll simulate some scenarios
        
        if random.random() < 0.02:  # 2% chance of new follow-up candidate
            # Simulate a lead that submitted a form but didn't schedule
            sample_lead = {
                "id": f"follow_candidate_{random.randint(1000, 9999)}",
                "name": random.choice(["Alex Johnson", "Maria Garcia", "Tom Wilson"]),
                "email": f"candidate{random.randint(1, 1000)}@example.com",
                "phone": f"+1555{random.randint(100, 999)}{random.randint(1000, 9999)}",
                "source": random.choice(["webform", "instagram"]),
                "qualification_score": random.randint(6, 9),
                "status": "no_response",
                "created_at": datetime.now() - timedelta(hours=random.randint(6, 48)),
                "last_contact": datetime.now() - timedelta(hours=random.randint(12, 72)),
                "notes": ["Filled out form but no response to initial email"]
            }
            
            await self.initiate_follow_up_sequence(sample_lead)
    
    async def initiate_follow_up_sequence(self, lead_data: Dict):
        """Start appropriate follow-up sequence for a lead"""
        source = lead_data["source"]
        status = lead_data["status"]
        
        # Determine which sequence to use
        if source == "webform" and status == "no_response":
            sequence_type = "form_no_schedule"
        elif source == "instagram" and status == "no_response":
            sequence_type = "instagram_no_response"
        else:
            sequence_type = "no_response_24h"
        
        sequence = self.follow_up_sequences[sequence_type]
        
        self.logger.info(f"Initiating {sequence_type} sequence for {lead_data['name']}")
        
        # Schedule all steps in the sequence
        for step_index, step in enumerate(sequence):
            scheduled_time = datetime.now() + timedelta(hours=step["delay_hours"])
            
            follow_up_task = {
                "lead": lead_data,
                "step": step,
                "step_index": step_index,
                "sequence_type": sequence_type,
                "scheduled_time": scheduled_time
            }
            
            self.pending_follow_ups.append(follow_up_task)
            
            self.logger.info(f"Scheduled {step['channel']} follow-up for {lead_data['name']} at {scheduled_time}")
    
    async def execute_follow_up_step(self, follow_up_task: Dict):
        """Execute a specific follow-up step"""
        lead = follow_up_task["lead"]
        step = follow_up_task["step"]
        channel = step["channel"]
        template = step["template"]
        
        self.logger.info(f"Executing follow-up: {template} via {channel} for {lead['name']}")
        
        # Execute based on channel
        if channel == "email":
            await self.send_email_follow_up(lead, template)
        elif channel == "sms":
            await self.send_sms_follow_up(lead, template)
        elif channel == "instagram":
            await self.send_instagram_follow_up(lead, template)
    
    async def send_email_follow_up(self, lead: Dict, template: str):
        """Send email follow-up using specified template"""
        email_templates = {
            "follow_up_1": {
                "subject": f"Quick question, {lead['name']}",
                "body": f"Hi {lead['name']},\n\nI wanted to follow up on our previous conversation. I know you expressed interest in improving your sales process.\n\nI have a few quick ideas that might help - would you be open to a brief call this week?\n\nBest regards,\nSales Team"
            },
            "immediate_follow_up": {
                "subject": f"Thanks for your submission, {lead['name']} - Next steps",
                "body": f"Hi {lead['name']},\n\nI just reviewed your form submission and I'm excited about the potential to help you achieve your goals.\n\nI noticed you haven't scheduled your consultation yet. Here's the direct link: [CALENDAR_LINK]\n\nThis consultation is completely free and typically provides immediate value.\n\nLooking forward to speaking with you!\nThe Team"
            },
            "reminder_to_schedule": {
                "subject": f"Don't miss out, {lead['name']}",
                "body": f"Hi {lead['name']},\n\nJust a friendly reminder that your complimentary consultation is still available.\n\nMany of our clients see immediate improvements after just one session.\n\nSchedule here: [CALENDAR_LINK]\n\nBest,\nThe Team"
            },
            "last_chance": {
                "subject": f"Last opportunity, {lead['name']}",
                "body": f"Hi {lead['name']},\n\nI don't want you to miss out on this opportunity. Based on your form submission, I believe we could really help you.\n\nThis is my final outreach - if you're interested, please schedule here: [CALENDAR_LINK]\n\nOtherwise, I'll remove you from our follow-up sequence.\n\nBest wishes,\nThe Team"
            },
            "value_proposition": {
                "subject": f"How we helped [Similar Company], {lead['name']}",
                "body": f"Hi {lead['name']},\n\nI wanted to share a quick case study that might interest you.\n\nWe recently helped a company similar to yours increase their sales by 300% in just 90 days.\n\nThe strategies we used might work for your situation too.\n\nInterested in learning more? Let's chat: [CALENDAR_LINK]\n\nBest,\nThe Team"
            }
        }
        
        template_data = email_templates.get(template, email_templates["follow_up_1"])
        
        # In production, integrate with email service (SendGrid, Mailgun, etc.)
        self.logger.info(f"Email sent to {lead['email']}")
        self.logger.info(f"Subject: {template_data['subject']}")
        self.logger.info(f"Template: {template}")
    
    async def send_sms_follow_up(self, lead: Dict, template: str):
        """Send SMS follow-up using specified template"""
        sms_templates = {
            "follow_up_2": f"Hi {lead['name']}, quick follow-up on your interest in our services. Still looking to improve your sales process? Reply YES for a quick call. - Sales Team",
            "reminder_to_schedule": f"Hi {lead['name']}, friendly reminder about your free consultation. Many clients see immediate value. Ready to schedule? Reply YES - The Team",
            "final_outreach": f"Hi {lead['name']}, this is my final message. If you're still interested in growing your business, reply YES and I'll call you today. Otherwise, I'll stop following up. - The Team"
        }
        
        message = sms_templates.get(template, sms_templates["follow_up_2"])
        
        # In production, integrate with SMS service (Twilio, etc.)
        self.logger.info(f"SMS sent to {lead['phone']}: {message}")
    
    async def send_instagram_follow_up(self, lead: Dict, template: str):
        """Send Instagram follow-up by coordinating with Instagram agent"""
        ig_templates = {
            "follow_up_3": f"Hey {lead['name']}! Hope you're doing well. I wanted to circle back about helping you with your sales goals. Still interested in chatting?",
            "gentle_reminder": f"Hi {lead['name']}! Just wanted to make sure you saw my previous message. I have some ideas that might help your business grow.",
            "final_outreach": f"Hi {lead['name']}, I don't want to be pushy, but I really think we could help you achieve your goals. If you're interested, just say 'yes' and I'll get you connected with the right person."
        }
        
        message = ig_templates.get(template, ig_templates["gentle_reminder"])
        
        # Send A2A message to Instagram agent to send the DM
        await self.send_a2a_message("Instagram", {
            "message_type": "send_follow_up_dm",
            "payload": {
                "lead": lead,
                "message": message,
                "template": template
            }
        })
        
        self.logger.info(f"Instagram follow-up coordinated for {lead['name']}")
    
    async def schedule_next_follow_up_step(self, completed_follow_up: Dict):
        """Schedule the next step in sequence if applicable"""
        sequence_type = completed_follow_up["sequence_type"]
        step_index = completed_follow_up["step_index"]
        sequence = self.follow_up_sequences[sequence_type]
        
        # Check if there are more steps in the sequence
        next_step_index = step_index + 1
        if next_step_index < len(sequence):
            lead = completed_follow_up["lead"]
            next_step = sequence[next_step_index]
            
            scheduled_time = datetime.now() + timedelta(hours=next_step["delay_hours"])
            
            next_follow_up = {
                "lead": lead,
                "step": next_step,
                "step_index": next_step_index,
                "sequence_type": sequence_type,
                "scheduled_time": scheduled_time
            }
            
            self.pending_follow_ups.append(next_follow_up)
            self.logger.info(f"Scheduled next follow-up step for {lead['name']}")
    
    async def handle_lead_response(self, lead_id: str, response_type: str):
        """Handle when a lead responds to follow-up"""
        # Remove pending follow-ups for this lead
        self.pending_follow_ups = [
            f for f in self.pending_follow_ups 
            if f["lead"]["id"] != lead_id
        ]
        
        if response_type == "positive":
            self.logger.info(f"Lead {lead_id} responded positively - stopping follow-up sequence")
            # Trigger booking sequence or hand off to human
        elif response_type == "negative":
            self.logger.info(f"Lead {lead_id} responded negatively - stopping follow-up sequence")
            # Remove from all sequences
        elif response_type == "scheduled":
            self.logger.info(f"Lead {lead_id} scheduled appointment - stopping follow-up sequence")
            # Mark as converted
    
    async def send_a2a_message(self, target_agent: str, message: Dict):
        """Send A2A protocol message to another agent"""
        a2a_message = {
            "from_agent": self.name,
            "to_agent": target_agent,
            "timestamp": datetime.now().isoformat(),
            **message
        }
        
        # In production, this would use ADK's A2A messaging
        self.logger.info(f"A2A Message to {target_agent}: {a2a_message['message_type']}")
    
    def get_agent_metrics(self) -> Dict:
        """Return FollowUp agent specific metrics"""
        return {
            "agent_name": self.name,
            "status": "running" if self.is_running else "stopped",
            "pending_follow_ups": len(self.pending_follow_ups),
            "sequence_types": list(self.follow_up_sequences.keys()),
            "monitoring_frequency": "5 minutes",
            "multi_channel": True
        }