#!/usr/bin/env python3
"""
Check if schedule was executed by checking last_run_at field
"""

import asyncio
import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session
from app.services.user_verification_schedule import VerificationScheduleService


async def check_execution():
    """Check if schedules have been executed"""
    async with async_session() as db:
        schedule_service = VerificationScheduleService(db)
        schedules = await schedule_service.get_all_schedules()
        
        print("=" * 70)
        print("📊 Schedule Execution Status")
        print("=" * 70)
        
        current_time = datetime.now()
        print(f"Current time: {current_time.strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        for schedule in schedules:
            status = "✅ ENABLED" if schedule.enabled else "❌ DISABLED"
            print(f"\n🔹 Schedule #{schedule.id} - {status}")
            print(f"   Time: {schedule.schedule_time}")
            print(f"   Interval: {schedule.interval_hours} hours")
            print(f"   Chat: {schedule.chat_id or 'All chats'}")
            
            if schedule.next_run_at:
                next_run = schedule.next_run_at
                if next_run <= current_time:
                    print(f"   Next run: {next_run} ⚡ SHOULD HAVE RUN!")
                else:
                    diff = (next_run - current_time).total_seconds()
                    minutes = int(diff / 60)
                    seconds = int(diff % 60)
                    print(f"   Next run: {next_run} (in {minutes}m {seconds}s)")
            
            if schedule.last_run_at:
                last_run = schedule.last_run_at
                diff = (current_time - last_run).total_seconds()
                minutes_ago = int(diff / 60)
                print(f"   Last run: {last_run} ({minutes_ago} minutes ago) ✅")
            else:
                print(f"   Last run: Never")
        
        print("\n" + "=" * 70)
        
        # Check if any schedules should have run
        ready = await schedule_service.get_schedules_to_run()
        if ready:
            print(f"⚠️  WARNING: {len(ready)} schedule(s) are ready but haven't run yet!")
            print("   This might mean:")
            print("   1. The backend was just started (schedules run every minute)")
            print("   2. The background task is not running")
            print("   3. There's an error in the background task")
        else:
            print("✅ All schedules are up to date")
        
        print("=" * 70)


if __name__ == "__main__":
    asyncio.run(check_execution())
