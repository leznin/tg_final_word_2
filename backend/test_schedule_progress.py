"""
Test script to manually trigger a schedule and check if progress bar works
"""
import asyncio
import time
from datetime import datetime
from sqlalchemy import select
from app.core.database import async_session
from app.models.user_verification_schedule import UserVerificationSchedule
from app.services.user_verification_schedule import VerificationScheduleService
from app.services.user_verification import UserVerificationService


async def test_schedule_with_progress():
    """Test running a schedule and monitoring progress"""
    async with async_session() as db:
        schedule_service = VerificationScheduleService(db)
        
        print("=" * 80)
        print("TESTING SCHEDULE VERIFICATION WITH PROGRESS BAR")
        print("=" * 80)
        print(f"Started at: {datetime.now()}")
        print()
        
        # Get first enabled schedule
        schedules = await schedule_service.get_enabled_schedules()
        if not schedules:
            print("❌ No enabled schedules found!")
            print("   Please create and enable a schedule in the web interface.")
            return
        
        schedule = schedules[0]
        print(f"✓ Found schedule #{schedule.id}")
        print(f"  Time: {schedule.schedule_time}")
        print(f"  Interval: {schedule.interval_hours} hours")
        print(f"  Chat: {schedule.chat.title if schedule.chat else 'All chats'}")
        print()
        
        # Import telegram bot
        from app.main import get_telegram_bot
        telegram_bot = get_telegram_bot()
        
        if not telegram_bot or not telegram_bot.is_running:
            print("❌ Telegram bot is not running!")
            print("   Please start the backend server first:")
            print("   uvicorn app.main:app --reload")
            return
        
        print("✓ Telegram bot is running")
        print()
        print("-" * 80)
        print("RUNNING VERIFICATION (this will take a few seconds)...")
        print("-" * 80)
        
        # Import verification router to use global instance
        import app.routers.user_verification as verification_router
        
        # Create or use global verification service instance
        if verification_router._verification_service_instance is None or \
           not verification_router._verification_service_instance.is_running:
            verification_router._verification_service_instance = UserVerificationService(
                telegram_bot.bot, db
            )
        
        verification_service = verification_router._verification_service_instance
        
        # Run verification in background
        async def run_verification():
            try:
                result = await verification_service.verify_all_active_users(
                    chat_id=schedule.chat_id,
                    auto_update=schedule.auto_update,
                    delay_between_requests=0.5
                )
                return result
            except Exception as e:
                print(f"Error: {e}")
                return None
        
        # Start verification task
        verification_task = asyncio.create_task(run_verification())
        
        # Monitor progress
        print("\nPROGRESS:")
        last_progress = 0
        while not verification_task.done():
            status = verification_service.get_status()
            if status['is_running'] and status['total_users'] > 0:
                progress = status['current_progress']
                if progress != last_progress:
                    percentage = status['progress_percentage']
                    total = status['total_users']
                    checked = status['checked_users']
                    updated = status['updated_users']
                    errors = status['users_with_errors']
                    
                    bar_length = 50
                    filled = int(bar_length * percentage / 100)
                    bar = '█' * filled + '░' * (bar_length - filled)
                    
                    print(f"[{bar}] {percentage:.1f}% | "
                          f"{checked}/{total} | "
                          f"✓{updated} ✗{errors}")
                    
                    last_progress = progress
            
            await asyncio.sleep(0.3)
        
        # Get result
        result = await verification_task
        
        if result:
            print()
            print("-" * 80)
            print("✅ VERIFICATION COMPLETED!")
            print("-" * 80)
            print(f"Total checked: {result.total_checked}")
            print(f"Total updated: {result.total_updated}")
            print(f"Total errors: {result.total_errors}")
            print(f"Total with changes: {result.total_with_changes}")
            print(f"Duration: {result.duration_seconds:.2f} seconds")
            print()
            
            # Update last run
            await schedule_service.update_last_run(schedule.id, datetime.now())
            print(f"✓ Updated schedule last_run_at")
        else:
            print("\n❌ Verification failed!")
        
        print()
        print("=" * 80)
        print("TEST COMPLETED")
        print("=" * 80)
        print("\nNOTE: Open the web interface and go to 'Проверка пользователей' ->")
        print("      'Расписания проверок' tab. The progress bar should appear there")
        print("      when a scheduled verification is running.")


if __name__ == "__main__":
    asyncio.run(test_schedule_with_progress())
