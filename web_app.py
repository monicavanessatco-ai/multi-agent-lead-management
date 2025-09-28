# web_app.py - Flask web application with Google Sheets integration

from flask import Flask, render_template, jsonify
import asyncio
import json
import threading
from datetime import datetime
import requests
import csv
from io import StringIO
import time

app = Flask(__name__)

# Global variables to store live data
live_metrics = {
    "leads_processed": 0,
    "qualified_leads": 0,
    "conversion_rate": 0.0,
    "active_agents": 3,
    "last_updated": datetime.now().isoformat()
}

live_leads = []
agent_status = {
    "Instagram": {"status": "running", "last_activity": "2 seconds ago", "leads_today": 0},
    "WebForm": {"status": "running", "last_activity": "1 minute ago", "leads_today": 0},
    "FollowUp": {"status": "running", "last_activity": "30 seconds ago", "sequences_active": 0}
}

recent_activities = []

class GoogleSheetsReader:
    def __init__(self, sheet_url):
        # Convert Google Sheets URL to CSV export URL
        if "/edit" in sheet_url:
            sheet_id = sheet_url.split("/d/")[1].split("/")[0]
            self.csv_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv&gid=0"
        else:
            self.csv_url = sheet_url
    
    def read_leads_data(self):
        """Read leads data from Google Sheets"""
        try:
            response = requests.get(self.csv_url)
            response.raise_for_status()
            
            # Parse CSV data
            csv_data = StringIO(response.text)
            reader = csv.DictReader(csv_data)
            
            leads = []
            for row in reader:
                # Skip empty rows
                if not any(row.values()):
                    continue
                    
                lead = {
                    "id": row.get("ID", ""),
                    "name": row.get("Name", ""),
                    "email": row.get("Email", ""),
                    "phone": row.get("Phone", ""),
                    "source": row.get("Source", ""),
                    "qualification_score": self.safe_int(row.get("Score", "0")),
                    "status": row.get("Status", "new"),
                    "created_at": row.get("Created", datetime.now().isoformat()),
                    "notes": row.get("Notes", "")
                }
                
                if lead["name"]:  # Only add if name is not empty
                    leads.append(lead)
            
            return leads
            
        except Exception as e:
            print(f"Error reading Google Sheets: {e}")
            return self.get_sample_data()
    
    def safe_int(self, value):
        """Safely convert string to int"""
        try:
            return int(float(value)) if value else 0
        except (ValueError, TypeError):
            return 0
    
    def get_sample_data(self):
        """Fallback sample data if sheets unavailable"""
        return [
            {
                "id": "sample_001",
                "name": "John Smith",
                "email": "john@example.com",
                "phone": "+1234567890",
                "source": "instagram",
                "qualification_score": 8,
                "status": "qualified",
                "created_at": datetime.now().isoformat(),
                "notes": "High-value prospect from Instagram"
            },
            {
                "id": "sample_002", 
                "name": "Sarah Johnson",
                "email": "sarah@business.com",
                "phone": "+1987654321",
                "source": "webform",
                "qualification_score": 9,
                "status": "scheduled",
                "created_at": datetime.now().isoformat(),
                "notes": "CEO interested in scaling sales"
            }
        ]

# Initialize Google Sheets reader
sheets_reader = GoogleSheetsReader("https://docs.google.com/spreadsheets/d/16xTiEfwP8E6CNC0zfoImscsnDSuUezrW2vj_MvRq8Kw/edit?usp=sharing")

def update_live_data():
    """Background task to update live data"""
    global live_leads, live_metrics, agent_status, recent_activities
    
    while True:
        try:
            # Read fresh data from Google Sheets
            leads = sheets_reader.read_leads_data()
            live_leads = leads
            
            # Calculate metrics
            total_leads = len(leads)
            qualified_leads = len([l for l in leads if l["qualification_score"] >= 7])
            conversion_rate = (qualified_leads / total_leads * 100) if total_leads > 0 else 0
            
            live_metrics.update({
                "leads_processed": total_leads,
                "qualified_leads": qualified_leads,
                "conversion_rate": round(conversion_rate, 1),
                "active_agents": 3,
                "last_updated": datetime.now().isoformat()
            })
            
            # Update agent status with lead counts
            instagram_leads = len([l for l in leads if l["source"] == "instagram"])
            webform_leads = len([l for l in leads if l["source"] == "webform"])
            
            agent_status["Instagram"]["leads_today"] = instagram_leads
            agent_status["WebForm"]["leads_today"] = webform_leads
            agent_status["FollowUp"]["sequences_active"] = len([l for l in leads if l["status"] == "follow_up"])
            
            # Add recent activity
            if leads:
                latest_lead = max(leads, key=lambda x: x["created_at"])
                activity = f"New {latest_lead['source']} lead: {latest_lead['name']} (Score: {latest_lead['qualification_score']}/10)"
                
                if activity not in [a["message"] for a in recent_activities[-5:]]:
                    recent_activities.append({
                        "timestamp": datetime.now().isoformat(),
                        "message": activity,
                        "type": "new_lead"
                    })
                    
                    # Keep only last 10 activities
                    recent_activities = recent_activities[-10:]
            
        except Exception as e:
            print(f"Error updating live data: {e}")
        
        time.sleep(10)  # Update every 10 seconds

# Routes
@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    return jsonify(live_metrics)

@app.route('/api/leads')
def get_leads():
    return jsonify(live_leads)

@app.route('/api/agents')
def get_agent_status():
    return jsonify(agent_status)

@app.route('/api/activities')
def get_activities():
    return jsonify(recent_activities)

@app.route('/api/charts/conversion')
def get_conversion_chart():
    """Data for conversion rate chart"""
    qualified = live_metrics["qualified_leads"]
    unqualified = live_metrics["leads_processed"] - qualified
    
    return jsonify({
        "labels": ["Qualified Leads", "Unqualified Leads"],
        "data": [qualified, unqualified],
        "backgroundColor": ["#4CAF50", "#FF9800"]
    })

@app.route('/api/charts/sources')
def get_sources_chart():
    """Data for lead sources chart"""
    sources = {}
    for lead in live_leads:
        source = lead["source"].title()
        sources[source] = sources.get(source, 0) + 1
    
    return jsonify({
        "labels": list(sources.keys()),
        "data": list(sources.values()),
        "backgroundColor": ["#2196F3", "#FF5722", "#9C27B0", "#607D8B"]
    })

if __name__ == '__main__':
    # Start background data update thread
    update_thread = threading.Thread(target=update_live_data, daemon=True)
    update_thread.start()
    
    # Start Flask app
    app.run(host='0.0.0.0', port=8081, debug=True)