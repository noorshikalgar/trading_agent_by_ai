import time
from datetime import datetime
from typing import Callable
from config import MARKET_OPEN, MARKET_CLOSE, TICK_INTERVAL_SECONDS

class SchedulerModule:
    """Controls agent loop timing and market hours."""
    
    def __init__(self, tick_callback: Callable):
        self.tick_callback = tick_callback
        self.running = False
        self.paused = False
    
    def is_market_hours(self) -> bool:
        """Check if current time is within market hours."""
        now = datetime.now().time()
        return MARKET_OPEN <= now <= MARKET_CLOSE
    
    def start(self):
        """Begin agent loop."""
        self.running = True
        self.paused = False
        
        print(f"🚀 Agent started at {datetime.now()}")
        
        while self.running:
            # Check if paused
            if self.paused:
                time.sleep(1)
                continue
            
            # Check market hours
            if not self.is_market_hours():
                print(f"⏸️ Outside market hours, waiting... "
                      f"({datetime.now().time()})")
                time.sleep(60)  # Check every minute
                continue
            
            # Execute tick callback
            try:
                self.tick_callback()
            except Exception as e:
                print(f"❌ Error in tick: {e}")
                # Could auto-pause here if desired
            
            # Sleep until next tick
            time.sleep(TICK_INTERVAL_SECONDS)
    
    def pause(self):
        """Pause agent loop (retains state)."""
        self.paused = True
        print("⏸️ Agent paused")
    
    def resume(self):
        """Resume from pause."""
        self.paused = False
        print("▶️ Agent resumed")
    
    def stop(self):
        """Stop agent loop completely."""
        self.running = False
        print("⏹️ Agent stopped")