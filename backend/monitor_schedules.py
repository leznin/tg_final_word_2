#!/usr/bin/env python3
"""
Monitor backend logs for schedule execution
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session
from app.services.user_verification_schedule import VerificationScheduleService


async def monitor_schedules():
    """Monitor schedules and show which ones are ready to run"""
    print("🔍 Monitoring schedules...")
    print("Press Ctrl+C to stop\n")
    
    while True:
        try:
            async with async_session() as db:
                schedule_service = VerificationScheduleService(db)
                
                # Get all enabled schedules
                enabled = await schedule_service.get_enabled_schedules()
                
                # Get schedules ready to run
                ready = await schedule_service.get_schedules_to_run()
                
                current_time = datetime.now()
                
                print(f"\r⏰ {current_time.strftime('%H:%M:%S')} | ", end="")
                print(f"Enabled: {len(enabled)} | ", end="")
                print(f"Ready to run: {len(ready)}", end="")
                
                if ready:
                    print(f" | 🚀 SCHEDULES READY:", end="")
                    for schedule in ready:
                        print(f" #{schedule.id}", end="")
                
                print("     ", end="", flush=True)
                
            await asyncio.sleep(5)  # Check every 5 seconds
            
        except KeyboardInterrupt:
            print("\n\n👋 Monitoring stopped")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(monitor_schedules())
