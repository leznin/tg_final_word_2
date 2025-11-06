"""
Diagnostic script to check verification schedule functionality
"""
import asyncio
from datetime import datetime
from sqlalchemy import select
from app.core.database import async_session
from app.models.user_verification_schedule import UserVerificationSchedule
from app.services.user_verification_schedule import VerificationScheduleService


async def check_schedules():
    """Check all verification schedules and their status"""
    async with async_session() as db:
        schedule_service = VerificationScheduleService(db)
        
        print("=" * 80)
        print("VERIFICATION SCHEDULE DIAGNOSTICS")
        print("=" * 80)
        print(f"Current time: {datetime.now()}")
        print()
        
        # Get all schedules
        all_schedules = await schedule_service.get_all_schedules()
        print(f"Total schedules: {len(all_schedules)}")
        print()
        
        if not all_schedules:
            print("❌ No schedules found!")
            print("   Create a schedule in the web interface first.")
            return
        
        for schedule in all_schedules:
            print(f"Schedule #{schedule.id}")
            print(f"  Status: {'✅ ENABLED' if schedule.enabled else '❌ DISABLED'}")
            print(f"  Time: {schedule.schedule_time}")
            print(f"  Interval: {schedule.interval_hours} hours")
            print(f"  Auto Update: {schedule.auto_update}")
            print(f"  Chat: {schedule.chat.title if schedule.chat else 'All chats'}")
            print(f"  Last Run: {schedule.last_run_at or 'Never'}")
            print(f"  Next Run: {schedule.next_run_at or 'Not calculated'}")
            
            if schedule.next_run_at:
                time_diff = (schedule.next_run_at - datetime.now()).total_seconds()
                if time_diff > 0:
                    hours = int(time_diff // 3600)
                    minutes = int((time_diff % 3600) // 60)
                    print(f"  Time until next run: {hours}h {minutes}m")
                else:
                    print(f"  ⚠️  SHOULD RUN NOW! (overdue by {abs(int(time_diff))} seconds)")
            print()
        
        # Get schedules that should run now
        print("-" * 80)
        schedules_to_run = await schedule_service.get_schedules_to_run()
        print(f"Schedules ready to run now: {len(schedules_to_run)}")
        
        if schedules_to_run:
            print("\n🔥 These schedules should be running:")
            for schedule in schedules_to_run:
                print(f"  - Schedule #{schedule.id}: {schedule.schedule_time}, "
                      f"Chat: {schedule.chat.title if schedule.chat else 'All'}")
        else:
            print("  ✓ No schedules need to run right now")
        
        print("\n" + "=" * 80)
        print("CHECKING BACKGROUND TASK")
        print("=" * 80)
        print("\nTo verify the background task is running:")
        print("1. Check backend logs for: 'Started scheduled user verification task'")
        print("2. Look for periodic checks (every 60 seconds)")
        print("3. When schedule time matches, you should see:")
        print("   - 'Found X verification schedule(s) to run'")
        print("   - 'Running verification schedule X'")
        print("   - 'Verification schedule X completed: ...'")
        print()


if __name__ == "__main__":
    asyncio.run(check_schedules())
