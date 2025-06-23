# Render-Compatible Trading Agent with Health Check Endpoint
import os
import time
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from flask import Flask, jsonify
import pytz

class RenderOptimizer:
    def __init__(self):
        self.est = pytz.timezone('US/Eastern')
        self.is_running = False
        self.last_update = None
        self.status_message = "Initializing..."
        self.last_alerts = []
        self.alert_count = 0
        print("🎨 Render Deployment Mode - Optimized for 750 free hours/month")
        
    def should_run_now(self):
        """Determine if the trading agent should run based on current time"""
        now = datetime.now(self.est)
        
        if self.is_market_hours(now):
            return {
                'should_run': True,
                'check_interval': 10,  # minutes - frequent during market hours
                'message': '🟢 Active market monitoring (9:30AM-4PM ET)',
                'next_check': now + timedelta(minutes=10)
            }
        elif self.is_extended_hours(now):
            return {
                'should_run': True,
                'check_interval': 60,  # hourly during extended hours
                'message': '🟡 Extended hours monitoring (7AM-8PM ET)',
                'next_check': now + timedelta(hours=1)
            }
        else:
            # Sleep for 4 hours during off-hours to save resources
            next_check = self.get_next_extended_open(now)
            return {
                'should_run': False,
                'sleep_minutes': 240,  # 4 hours
                'message': f'😴 Deep sleep mode - Next check at {next_check.strftime("%I:%M %p ET")}',
                'next_check': next_check
            }
    
    def is_market_hours(self, dt):
        """9:30 AM - 4:00 PM ET, Monday-Friday"""
        if dt.weekday() >= 5:  # Weekend
            return False
        
        market_open = dt.replace(hour=9, minute=30, second=0, microsecond=0)
        market_close = dt.replace(hour=16, minute=0, second=0, microsecond=0)
        
        return market_open <= dt <= market_close
    
    def is_extended_hours(self, dt):
        """7:00 AM - 8:00 PM ET, Monday-Friday (includes pre/post market)"""
        if dt.weekday() >= 5:  # Weekend
            return False
        
        extended_open = dt.replace(hour=7, minute=0, second=0, microsecond=0)
        extended_close = dt.replace(hour=20, minute=0, second=0, microsecond=0)
        
        return extended_open <= dt <= extended_close
    
    def get_next_extended_open(self, dt):
        """Get the next extended market open time"""
        # If it's Friday evening or weekend, next open is Monday 7 AM
        if dt.weekday() == 4 and dt.hour >= 20:  # Friday after 8 PM
            days_to_add = 3  # To Monday
        elif dt.weekday() >= 5:  # Weekend
            days_to_add = 7 - dt.weekday()  # Days until Monday
        else:  # Weekday
            if dt.hour >= 20:  # After 8 PM, next day
                days_to_add = 1
            else:  # Same day
                days_to_add = 0
        
        next_open = (dt + timedelta(days=days_to_add)).replace(
            hour=7, minute=0, second=0, microsecond=0
        )
        return next_open
    
    def log_status(self):
        """Log current optimization status"""
        status = self.should_run_now()
        timestamp = datetime.now(self.est).strftime('%Y-%m-%d %I:%M:%S %p ET')
        
        print(f"\n⏰ {timestamp}")
        print(f"📊 {status['message']}")
        
        # Update instance variables for health check
        self.last_update = timestamp
        self.status_message = status['message']
        
        if status['should_run']:
            print(f"🔄 Next check in {status['check_interval']} minutes")
        else:
            print(f"💤 Sleeping for {status['sleep_minutes']} minutes")
        
        return status

def analyze_mag7_stocks():
    """Analyze MAG7 stocks for strong buy signals"""
    # TODO: Replace with your actual analysis logic
    # This is where you'd integrate:
    # - Technical indicators (RSI, MACD, etc.)
    # - Fundamental analysis
    # - News sentiment
    # - Volume analysis
    
    # Mock strong buy detection for example
    mag7_symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META']
    
    # Simulate finding strong buys (replace with real logic)
    import random
    if random.random() < 0.1:  # 10% chance for demo
        return [{'symbol': random.choice(mag7_symbols), 'signal': 'STRONG BUY', 'confidence': 0.85}]
    
    return []

def send_email_alert(strong_buys):
    """Send email alert for strong buy signals"""
    try:
        # Email configuration from environment variables
        smtp_server = os.environ.get('SMTP_SERVER', 'smtp.gmail.com')
        smtp_port = int(os.environ.get('SMTP_PORT', '587'))
        sender_email = os.environ.get('SENDER_EMAIL')
        sender_password = os.environ.get('SENDER_PASSWORD')  # Use app password for Gmail
        recipient_email = os.environ.get('RECIPIENT_EMAIL')
        
        if not all([sender_email, sender_password, recipient_email]):
            print("❌ Email configuration missing. Set SENDER_EMAIL, SENDER_PASSWORD, RECIPIENT_EMAIL")
            return
        
        # Create email content
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = f"🚀 MAG7 Strong Buy Alert - {len(strong_buys)} Signal(s)"
        
        body = "MAG7 Trading Agent Alert\n\n"
        for buy in strong_buys:
            body += f"📈 {buy['symbol']}: {buy['signal']} (Confidence: {buy['confidence']:.0%})\n"
        
        body += f"\nTimestamp: {datetime.now(pytz.timezone('US/Eastern')).strftime('%Y-%m-%d %I:%M:%S %p ET')}"
        body += f"\nAgent Status: Active"
        
        msg.attach(MIMEText(body, 'plain'))
        
        # Send email
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        
        # Update optimizer stats
        optimizer.last_alerts = strong_buys
        optimizer.alert_count += len(strong_buys)
        
        print(f"✅ Email alert sent successfully to {recipient_email}")
        
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Global optimizer instance
optimizer = RenderOptimizer()

# Flask app for health check endpoint
app = Flask(__name__)

@app.route('/')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({
        'status': 'healthy',
        'service': 'Mag7 Trading Agent',
        'last_update': optimizer.last_update,
        'current_status': optimizer.status_message,
        'is_running': optimizer.is_running,
        'timestamp': datetime.now(optimizer.est).isoformat()
    })

@app.route('/status')
def detailed_status():
    """Detailed status endpoint"""
    current_status = optimizer.should_run_now()
    return jsonify({
        'service': 'Mag7 Trading Agent',
        'current_time': datetime.now(optimizer.est).isoformat(),
        'should_run': current_status['should_run'],
        'message': current_status['message'],
        'next_check': current_status.get('next_check', '').isoformat() if current_status.get('next_check') else None,
        'is_market_hours': optimizer.is_market_hours(datetime.now(optimizer.est)),
        'is_extended_hours': optimizer.is_extended_hours(datetime.now(optimizer.est)),
        'total_alerts_sent': optimizer.alert_count,
        'last_alerts': optimizer.last_alerts
    })

@app.route('/test-alert')
def test_alert():
    """Test email alert system"""
    test_alert = [{'symbol': 'TEST', 'signal': 'STRONG BUY', 'confidence': 0.99}]
    send_email_alert(test_alert)
    return jsonify({'message': 'Test alert sent', 'status': 'success'})

def trading_agent_worker():
    """Background worker for trading logic"""
    print("🚀 Starting Mag7 Trading Agent Background Worker")
    optimizer.is_running = True
    
    while optimizer.is_running:
        try:
            status = optimizer.log_status()
            
            if status['should_run']:
                print("📈 Executing trading logic...")
                
                # YOUR TRADING AGENT CODE GOES HERE
                strong_buys = analyze_mag7_stocks()
                
                if strong_buys:
                    send_email_alert(strong_buys)
                    print(f"📧 Email sent for {len(strong_buys)} strong buy signals")
                
                print("✅ Trading cycle completed")
                
                # Sleep until next check
                sleep_seconds = status['check_interval'] * 60
                print(f"⏳ Waiting {status['check_interval']} minutes until next check...")
                time.sleep(sleep_seconds)
                
            else:
                # Deep sleep mode to save Render hours
                sleep_seconds = status['sleep_minutes'] * 60
                print(f"💤 Entering deep sleep for {status['sleep_minutes']} minutes...")
                time.sleep(sleep_seconds)
                
        except Exception as e:
            print(f"❌ Trading Agent Error: {e}")
            print("🔄 Retrying in 5 minutes...")
            time.sleep(300)  # 5 minutes

def start_background_worker():
    """Start the trading agent in a background thread"""
    worker_thread = threading.Thread(target=trading_agent_worker, daemon=True)
    worker_thread.start()
    return worker_thread

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 Starting Render-Compatible Mag7 Trading Agent")
    print("=" * 60)
    
    # Start background trading worker
    worker = start_background_worker()
    
    # Get port from environment (Render provides this)
    port = int(os.environ.get('PORT', 5000))
    
    print(f"🌐 Starting health check server on port {port}")
    print(f"📊 Trading agent running in background thread")
    print(f"🔗 Health check: http://localhost:{port}/")
    print(f"📈 Status endpoint: http://localhost:{port}/status")
    
    # Run Flask app (this satisfies Render's port requirement)
    app.run(host='0.0.0.0', port=port, debug=False)
