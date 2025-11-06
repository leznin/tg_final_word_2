"""
Script to check scheduled posts in the database
"""

import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, and_
from app.core.database import async_session
from app.models.chat_posts import ChatPost


async def check_scheduled_posts():
    """Check all scheduled posts in the database"""
    async with async_session() as db:
        # Get all unsent posts
        query = select(ChatPost).where(
            and_(
                ChatPost.is_sent == False,
                ChatPost.is_deleted == False
            )
        )
        result = await db.execute(query)
        posts = result.scalars().all()
        
        now = datetime.now(timezone.utc)
        print(f"\n=== Current time (UTC): {now} ===\n")
        
        if not posts:
            print("No unsent posts found in database")
            return
        
        print(f"Found {len(posts)} unsent post(s):\n")
        
        for post in posts:
            print(f"Post ID: {post.id}")
            print(f"  Chat ID: {post.chat_id}")
            print(f"  Content: {post.content_text[:50] if post.content_text else 'No text'}...")
            print(f"  Scheduled send at: {post.scheduled_send_at}")
            print(f"  Is sent: {post.is_sent}")
            print(f"  Is deleted: {post.is_deleted}")
            print(f"  Created at: {post.created_at}")
            
            if post.scheduled_send_at:
                if post.scheduled_send_at.tzinfo is None:
                    print(f"  ⚠️  WARNING: scheduled_send_at is timezone-naive!")
                    # Try to compare as if it's UTC
                    aware_time = post.scheduled_send_at.replace(tzinfo=timezone.utc)
                    time_diff = (aware_time - now).total_seconds()
                else:
                    time_diff = (post.scheduled_send_at - now).total_seconds()
                
                if time_diff <= 0:
                    print(f"  ✅ Should be sent NOW (overdue by {abs(time_diff):.0f} seconds)")
                else:
                    print(f"  ⏰ Will be sent in {time_diff:.0f} seconds")
            else:
                print(f"  ❌ No scheduled_send_at time set")
            
            # Check reply_markup for invalid URLs
            if post.reply_markup:
                print(f"  Reply markup: {post.reply_markup}")
                for row in post.reply_markup.get('inline_keyboard', []):
                    for button in row.get('buttons', []):
                        if button.get('url'):
                            url = button['url']
                            if 'localhost' in url.lower() or '127.0.0.1' in url:
                                print(f"  ⚠️  WARNING: Button has localhost URL: {url}")
            
            print()


if __name__ == "__main__":
    asyncio.run(check_scheduled_posts())
