"""
Script to test and verify unpin scheduling functionality
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, and_
from app.core.database import async_session
from app.models.chat_posts import ChatPost


async def check_scheduled_unpins():
    """Check for posts scheduled to be unpinned"""
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        print(f"Current time (UTC): {now}")
        print("-" * 80)
        
        # Get all pinned posts with scheduled unpin time
        query = select(ChatPost).where(
            and_(
                ChatPost.is_pinned == True,
                ChatPost.scheduled_unpin_at.isnot(None),
                ChatPost.is_deleted == False
            )
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        if not posts:
            print("No pinned posts with scheduled unpin time found.")
            return
        
        print(f"Found {len(posts)} pinned post(s) with scheduled unpin:\n")
        
        for post in posts:
            time_until_unpin = post.scheduled_unpin_at - now
            is_ready = post.scheduled_unpin_at <= now
            
            print(f"Post ID: {post.id}")
            print(f"  Chat ID: {post.chat_id}")
            print(f"  Message ID: {post.telegram_message_id}")
            print(f"  Content: {post.content_text[:50] if post.content_text else 'No text'}...")
            print(f"  Sent at: {post.sent_at}")
            print(f"  Scheduled unpin at: {post.scheduled_unpin_at}")
            print(f"  Pin duration: {post.pin_duration_minutes} minutes")
            print(f"  Time until unpin: {time_until_unpin}")
            print(f"  Ready to unpin: {'✅ YES' if is_ready else '❌ NO'}")
            print("-" * 80)


async def main():
    await check_scheduled_unpins()


if __name__ == "__main__":
    asyncio.run(main())
