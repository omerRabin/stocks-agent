# Render-Only Resource Optimizer
import os
import time
from datetime import datetime, timedelta
import pytz

class RenderOptimizer:
    def __init__(self):
        self.est = pytz.timezone('US/Eastern')
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
        print(f"\n⏰ {datetime.now(self.est).strftime('%Y-%m-%d %I:%M:%S %p ET')}")
        print(f"📊 {status['message']}")
        
        if status['should_run']:
            print(f"🔄 Next check in {status['check_interval']} minutes")
        else:
            print(f"💤 Sleeping for {status['sleep_minutes']} minutes")
        
        return status

# Example usage in your main trading agent
def main_trading_loop():
    """Main loop for your trading agent"""
    optimizer = RenderOptimizer()
    
    print("🚀 Starting Mag7 Trading Agent on Render")
    print("=" * 50)
    
    while True:
        try:
            status = optimizer.log_status()
            
            if status['should_run']:
                print("📈 Executing trading logic...")
                
                # YOUR TRADING AGENT CODE GOES HERE
                # Example:
                # - Fetch market data
                # - Analyze stocks
                # - Send alerts
                # - Update database
                
                # Simulate trading work
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
                
        except KeyboardInterrupt:
            print("\n🛑 Trading agent stopped by user")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("🔄 Retrying in 5 minutes...")
            time.sleep(300)  # 5 minutes

if __name__ == "__main__":
    main_trading_loop()
