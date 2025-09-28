#!/usr/bin/env python3
"""
Multi-Agent Lead Management System
Google Cloud A2A/ADK Challenge Implementation
"""

import asyncio
import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

@dataclass
class Lead:
    id: str
    name: str
    email: str
    phone: str
    source: str  # "instagram", "webform", "referral"
    qualification_score: int  # 1-10
    status: str  # "new", "contacted", "qualified", "scheduled", "closed"
    created_at: datetime
    last_contact: Optional[datetime] = None
    notes: List[str] = None
    
    def to_dict(self):
        return {
            **asdict(self),
            'created_at': self.created_at.isoformat(),
            'last_contact': self.last_contact.isoformat() if self.last_contact else None
        }

class BaseAgent:
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, config: Dict):
        self.name = name
        self.config = config
        self.is_running = False
        self.logger = logging.getLogger(f"Agent.{name}")
    
    async def start(self):
        self.is_running = True
        self.logger.info(f"{self.name} agent started")
    
    async def stop(self):
        self.is_running = False
        self.logger.info(f"{self.name} agent stopped")
    
    async def process_lead(self, lead: Lead) -> Lead:
        """Override in subclasses"""
        return lead

class AgentOrchestrator:
    """Main orchestrator managing all agents using A2A protocol"""
    
    def __init__(self):
        self.agents = {}
        self.leads_database = []
        self.metrics = {
            "leads_processed": 0,
            "qualified_leads": 0,
            "appointments_scheduled": 0,
            "response_time_avg": 0
        }
        self.logger = logging.getLogger("Orchestrator")
    
    async def initialize_agents(self):
        """Initialize and start all agents"""
        from agents.instagram_agent import InstagramAgent
        from agents.webform_agent import WebFormAgent
        from agents.followup_agent import FollowUpAgent
        
        config = {
            "instagram": {"api_key": "demo_ig_api_key"},
            "webform": {"typeform_webhook": "demo_webhook_url"},
            "followup": {"email_api": "demo_email_api"}
        }
        
        self.agents = {
            "instagram": InstagramAgent(config["instagram"]),
            "webform": WebFormAgent(config["webform"]),
            "followup": FollowUpAgent(config["followup"])
        }
        
        for agent in self.agents.values():
            await agent.start()
    
    async def run_parallel_agents(self):
        """Run all agents in parallel using continuous loops"""
        tasks = []
        
        for agent_name, agent in self.agents.items():
            task = asyncio.create_task(agent.continuous_monitor())
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def process_lead_handoff(self, lead: Lead, from_agent: str, to_agent: str):
        """Handle lead handoff between agents using A2A protocol"""
        self.logger.info(f"Handing off lead {lead.id} from {from_agent} to {to_agent}")
        
        lead.status = f"transferred_to_{to_agent}"
        self.leads_database.append(lead)
        
        self.metrics["leads_processed"] += 1
        if lead.qualification_score >= 7:
            self.metrics["qualified_leads"] += 1
    
    def get_performance_metrics(self) -> Dict:
        """Return system performance metrics"""
        return {
            **self.metrics,
            "conversion_rate": (self.metrics["qualified_leads"] / max(self.metrics["leads_processed"], 1)) * 100,
            "active_agents": len([a for a in self.agents.values() if a.is_running]),
            "system_uptime": "24/7"
        }

async def main():
    """Main entry point"""
    logging.basicConfig(level=logging.INFO)
    
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize_agents()
    
    print("Multi-Agent Lead Management System Started")
    print("All agents running in continuous loops...")
    
    try:
        await orchestrator.run_parallel_agents()
    except KeyboardInterrupt:
        print("Shutting down agents...")
        for agent in orchestrator.agents.values():
            await agent.stop()

if __name__ == "__main__":
    asyncio.run(main())