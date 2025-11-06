"""
Fix old scheduled posts with incorrect timezone
"""

import asyncio
from datetime import datetime, timezone, timedelta
from app.core.database import async_session
from sqlalchemy import select, text
from app.models.chat_posts import ChatPost


async def fix_old_posts():
    """Fix old posts that were saved with incorrect timezone"""
    print("="*70)
    print("FIXING OLD SCHEDULED POSTS")
    print("="*70)
    
    async with async_session() as db:
        # Get all unsent scheduled posts
        query = select(ChatPost).where(
            ChatPost.is_sent == False,
            ChatPost.scheduled_send_at.isnot(None),
            ChatPost.is_deleted == False
        ).order_by(ChatPost.id)
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        print(f"\nFound {len(posts)} unsent scheduled posts\n")
        
        now_utc = datetime.now(timezone.utc)
        print(f"Current UTC time: {now_utc}\n")
        
        for post in posts:
            scheduled_time = post.scheduled_send_at
            
            # Make timezone-aware if needed
            if scheduled_time.tzinfo is None:
                scheduled_time_utc = scheduled_time.replace(tzinfo=timezone.utc)
            else:
                scheduled_time_utc = scheduled_time
            
            print(f"Post ID: {post.id}")
            print(f"  Scheduled time (DB): {post.scheduled_send_at}")
            print(f"  Scheduled time (UTC): {scheduled_time_utc}")
            print(f"  Time diff: {(scheduled_time_utc - now_utc).total_seconds()} seconds")
            
            # If time is in the past, this was likely saved with wrong timezone
            if scheduled_time_utc < now_utc:
                # Assume it was GMT+4 local time stored as UTC
                # Convert: DB time is actually GMT+4, so subtract 4 hours to get real UTC
                correct_utc_time = scheduled_time_utc - timedelta(hours=4)
                
                print(f"  ⚠️  Time is in the past!")
                print(f"  Assuming it was GMT+4 saved as UTC")
                print(f"  Correct UTC time should be: {correct_utc_time}")
                print(f"  Time until send: {(correct_utc_time - now_utc).total_seconds()} seconds")
                
                # Ask if we should fix it
                print(f"  Options:")
                print(f"    1. Fix time (set to {correct_utc_time})")
                print(f"    2. Mark as deleted (skip this post)")
                print(f"    3. Send immediately (set time to now)")
                
                # For automation, let's mark old posts as deleted if they're way in the past
                if correct_utc_time < now_utc:
                    print(f"  → Even corrected time is in the past, marking as deleted")
                    post.is_deleted = True
                    await db.commit()
            else:
                print(f"  ✅ Time is in the future, will send normally")
            
            print()
        
        print("="*70)
        print("Done!")
        print("="*70)


if __name__ == "__main__":
    asyncio.run(fix_old_posts())
