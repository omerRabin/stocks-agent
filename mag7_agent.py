# Free Tier Resource Optimizer
import os
import time
from datetime import datetime, timedelta
import pytz

class FreeTierOptimizer:
    def __init__(self):
        self.est = pytz.timezone('US/Eastern')
        self.deploy_mode = os.getenv('DEPLOY_MODE', 'render')  # railway, cloudrun, render
        
    def optimize_for_platform(self):
        """Optimize based on deployment platform"""
        
        if self.deploy_mode == 'railway':
            return self.railway_optimization()
        elif self.deploy_mode == 'cloudrun':
            return self.cloudrun_optimization()
        elif self.deploy_mode == 'render':
            return self.render_optimization()
        else:
            return self.default_optimization()
    
    def railway_optimization(self):
        """Railway: 500 hours/month = ~16.6 hours/day"""
        print("🚂 Railway Optimization Mode")
        
        # Run only during extended market hours (8 AM - 6 PM ET)
        now = datetime.now(self.est)
        
        extended_open = now.replace(hour=8, minute=0, second=0)
        extended_close = now.replace(hour=18, minute=0, second=0)
        
        if extended_open <= now <= extended_close and now.weekday() < 5:
            return {
                'should_run': True,
                'check_interval': 15,  # minutes
                'message': '🟢 Running in extended hours (8AM-6PM ET)'
            }
        else:
            return {
                'should_run': False,
                'sleep_until': extended_open + timedelta(days=1 if now.hour >= 18 else 0),
                'message': '😴 Sleeping until extended market hours'
            }
    
    def cloudrun_optimization(self):
        """Cloud Run: Perfect for scheduled runs"""
        print("☁️ Cloud Run Optimization Mode")
        
        # Run every 30 minutes during market hours only
        now = datetime.now(self.est)
        
        if self.is_market_hours(now):
            return {
                'should_run': True,
                'check_interval': 30,  # minutes
                'message': '🟢 Cloud Run scheduled execution'
            }
        else:
            return {
                'should_run': False,
                'message': '⏸️ Waiting for next scheduled run'
            }
    
    def render_optimization(self):
        """Render: 750 hours/month = ~25 hours/day"""
        print("🎨 Render Optimization Mode")
        
        # Can run almost 24/7, but optimize for market hours
        now = datetime.now(self.est)
        
        if self.is_market_hours(now):
            return {
                'should_run': True,
                'check_interval': 10,  # minutes - more frequent
                'message': '🟢 Active market monitoring'
            }
        elif self.is_extended_hours(now):
            return {
                'should_run': True,
                'check_interval': 60,  # hourly during extended hours
                'message': '🟡 Extended hours monitoring'
            }
        else:
            return {
                'should_run': False,
                'sleep_minutes': 240,  # 4 hours
                'message': '😴 Deep sleep mode'
            }
    
    def is_market_hours(self, dt):
        """9:30 AM - 4:00 PM ET, Monday-Friday"""
        if dt.weekday() >= 5:  # Weekend
            return False
        
        market_open = dt.replace(hour=9, minute=30, second=0)
        market_close = dt.replace(hour=16, minute=0, second=0)
        
        return market_open <= dt <= market_close
    
    def is_extended_hours(self, dt):
        """7:00 AM - 8:00 PM ET, Monday-Friday"""
        if dt.weekday() >= 5:  # Weekend
            return False
        
        extended_open = dt.replace(hour=7, minute=0, second=0)
        extended_close = dt.replace(hour=20, minute=0, second=0)
        
        return extended_open <= dt <= extended_close

# Deployment Configuration Files

# 1. Railway deployment
railway_config = {
    "railway.json": {
        "$schema": "https://railway.app/railway.schema.json",
        "build": {
            "builder": "NIXPACKS"
        },
        "deploy": {
            "startCommand": "python mag7_agent.py",
            "restartPolicyType": "ON_FAILURE"
        }
    }
}

# 2. Google Cloud Run
cloudrun_config = {
    "cloudbuild.yaml": """
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/mag7-agent', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/mag7-agent']
- name: 'gcr.io/google.com/cloudsdktool/cloud-sdk'
  entrypoint: gcloud
  args: [
    'run', 'deploy', 'mag7-agent',
    '--image', 'gcr.io/$PROJECT_ID/mag7-agent',
    '--region', 'us-central1',
    '--platform', 'managed',
    '--allow-unauthenticated'
  ]
""",
    
    "Dockerfile": """
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV DEPLOY_MODE=cloudrun

CMD ["python", "mag7_agent.py"]
"""
}

# 3. Render deployment
render_config = {
    "render.yaml": """
services:
  - type: web
    name: mag7-agent
    env: python
    plan: free
    buildCommand: pip install -r requirements.txt
    startCommand: python mag7_agent.py
    envVars:
      - key: DEPLOY_MODE
        value: render
      - key: NEWS_API_KEY
        sync: false
      - key: EMAIL_FROM
        sync: false
      - key: EMAIL_PASSWORD
        sync: false
"""
}

# Quick deployment commands
deployment_commands = {
    "railway": [
        "# 1. Install Railway CLI",
        "npm install -g @railway/cli",
        "",
        "# 2. Login and deploy", 
        "railway login",
        "railway link",  # Link to existing project or create new
        "railway up",    # Deploy
        "",
        "# 3. Set environment variables",
        "railway variables set NEWS_API_KEY=your_key_here",
        "railway variables set EMAIL_FROM=your_email@gmail.com",
        "railway variables set EMAIL_PASSWORD=your_app_password"
    ],
    
    "cloudrun": [
        "# 1. Enable APIs",
        "gcloud services enable run.googleapis.com",
        "gcloud services enable cloudbuild.googleapis.com",
        "",
        "# 2. Deploy",
        "gcloud builds submit --config cloudbuild.yaml",
        "",
        "# 3. Set up Cloud Scheduler (runs every 15 min during market hours)",
        "gcloud scheduler jobs create http mag7-job \\",
        "  --schedule='*/15 9-16 * * 1-5' \\", 
        "  --time-zone='America/New_York' \\",
        "  --uri='https://YOUR_CLOUDRUN_URL' \\",
        "  --http-method=GET"
    ],
    
    "render": [
        "# 1. Connect GitHub repo to Render",
        "# 2. Create new Web Service",
        "# 3. Use these settings:",
        "#    - Environment: Python",  
        "#    - Build Command: pip install -r requirements.txt",
        "#    - Start Command: python mag7_agent.py",
        "# 4. Add environment variables in Render dashboard"
    ]
}

print("🚀 Free Deployment Options for Mag7 Trading Agent")
print("=" * 60)

print("\n1. 🏆 RAILWAY (Recommended)")
print("   ✅ 500 hours/month free")
print("   ✅ Always-on, no sleeping")
print("   ✅ Easy GitHub integration")
print("   ✅ Built-in environment variables")

print("\n2. ☁️ GOOGLE CLOUD RUN") 
print("   ✅ 2M requests/month free")
print("   ✅ Perfect for scheduled runs")
print("   ✅ Enterprise reliability")
print("   ✅ Automatic scaling")

print("\n3. 🎨 RENDER")
print("   ✅ 750 hours/month free") 
print("   ✅ Simple deployment")
print("   ✅ Good for continuous running")
print("   ✅ Free SSL certificates")

print("\nChoose your preferred platform and follow the deployment guide!")
