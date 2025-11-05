#!/usr/bin/env python3
"""
Test script to create a test schedule and verify it runs
"""

import asyncio
import sys
import os
from datetime import datetime, time, timedelta

# Add the app directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import async_session
from app.services.user_verification_schedule import VerificationScheduleService
from app.schemas.user_verification_schedule import VerificationScheduleCreate


async def create_test_schedule():
    """Create a test schedule that runs every minute for testing"""
    async with async_session() as db:
        schedule_service = VerificationScheduleService(db)
        
        # Get current time and add 1 minute
        current_time = datetime.now()
        test_time = (current_time + timedelta(minutes=1)).time()
        
        print(f"📅 Creating test schedule...")
        print(f"   Current time: {current_time.strftime('%H:%M:%S')}")
        print(f"   Schedule time: {test_time.strftime('%H:%M:%S')}")
        print(f"   Interval: 1 hour")
        
        # Create schedule
        schedule_data = VerificationScheduleCreate(
            enabled=True,
            schedule_time=test_time,
            interval_hours=1,  # Every hour
            auto_update=True,
            chat_id=None  # All chats
        )
        
        schedule = await schedule_service.create_schedule(schedule_data)
        
        print(f"\n✅ Test schedule created successfully!")
        print(f"   ID: {schedule.id}")
        print(f"   Enabled: {schedule.enabled}")
        print(f"   Time: {schedule.schedule_time}")
        print(f"   Next run: {schedule.next_run_at}")
        print(f"\n⏰ The schedule should run in approximately 1 minute...")
        print(f"   Watch the backend logs for: 'Running verification schedule {schedule.id}'")
        
        return schedule


async def list_schedules():
    """List all existing schedules"""
    async with async_session() as db:
        schedule_service = VerificationScheduleService(db)
        schedules = await schedule_service.get_all_schedules()
        
        if not schedules:
            print("📋 No schedules found")
            return
        
        print(f"\n📋 Found {len(schedules)} schedule(s):")
        for schedule in schedules:
            status = "✅ ENABLED" if schedule.enabled else "❌ DISABLED"
            print(f"\n   ID: {schedule.id} - {status}")
            print(f"   Time: {schedule.schedule_time}")
            print(f"   Interval: {schedule.interval_hours} hours")
            print(f"   Auto-update: {schedule.auto_update}")
            print(f"   Chat: {schedule.chat_id or 'All chats'}")
            if schedule.last_run_at:
                print(f"   Last run: {schedule.last_run_at}")
            if schedule.next_run_at:
                print(f"   Next run: {schedule.next_run_at}")


async def main():
    """Main test function"""
    print("=" * 60)
    print("🧪 Schedule Verification Test")
    print("=" * 60)
    
    # List existing schedules
    await list_schedules()
    
    # Ask user what to do
    print("\n" + "=" * 60)
    print("Options:")
    print("1. Create a new test schedule (runs in 1 minute)")
    print("2. Just list schedules")
    choice = input("Enter your choice (1 or 2): ").strip()
    
    if choice == "1":
        await create_test_schedule()
        print("\n" + "=" * 60)
        print("💡 Tips:")
        print("   - Keep this window open")
        print("   - Watch the backend terminal for log messages")
        print("   - You should see 'Found X verification schedule(s) to run'")
        print("   - Then 'Running verification schedule X'")
        print("   - Finally 'Verification schedule X completed: ...'")
        print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
