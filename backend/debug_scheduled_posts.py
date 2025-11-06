"""
Debug script to check scheduled posts and their times
"""

import asyncio
from datetime import datetime, timezone
from app.core.database import async_session
from sqlalchemy import select, text
from app.models.chat_posts import ChatPost

async def check_scheduled_posts():
    """Check scheduled posts and their timezone information"""
    async with async_session() as db:
        # Get current time
        now_utc = datetime.now(timezone.utc)
        now_naive = datetime.now()
        
        print("="*70)
        print("CURRENT TIME DEBUG")
        print("="*70)
        print(f"Server time (UTC aware):   {now_utc}")
        print(f"Server time (naive):       {now_naive}")
        print(f"Timezone info:             {now_utc.tzinfo}")
        print()
        
        # Get all unsent scheduled posts
        query = select(ChatPost).where(
            ChatPost.is_sent == False,
            ChatPost.scheduled_send_at.isnot(None),
            ChatPost.is_deleted == False
        ).order_by(ChatPost.id)
        
        result = await db.execute(query)
        posts = result.scalars().all()
        
        print("="*70)
        print(f"SCHEDULED POSTS (Total: {len(posts)})")
        print("="*70)
        
        if not posts:
            print("No scheduled posts found")
            return
        
        for post in posts:
            scheduled_time = post.scheduled_send_at
            
            print(f"\nPost ID: {post.id}")
            print(f"  Chat ID: {post.chat_id}")
            print(f"  Created at: {post.created_at}")
            print(f"  Scheduled send at: {scheduled_time}")
            print(f"  Scheduled time type: {type(scheduled_time)}")
            print(f"  Has timezone info: {scheduled_time.tzinfo is not None}")
            print(f"  Timezone: {scheduled_time.tzinfo}")
            
            # Try to make timezone aware if needed
            if scheduled_time.tzinfo is None:
                scheduled_time_utc = scheduled_time.replace(tzinfo=timezone.utc)
                print(f"  Scheduled time (as UTC): {scheduled_time_utc}")
                time_diff = scheduled_time_utc - now_utc
            else:
                time_diff = scheduled_time - now_utc
            
            print(f"  Time until send: {time_diff}")
            print(f"  Should send now: {time_diff.total_seconds() <= 0}")
            print(f"  is_sent: {post.is_sent}")
            print(f"  is_deleted: {post.is_deleted}")
            
            # Show raw database value
            raw_query = text(f"SELECT scheduled_send_at FROM chat_posts WHERE id = {post.id}")
            raw_result = await db.execute(raw_query)
            raw_value = raw_result.scalar()
            print(f"  Raw DB value: {raw_value}")
            print(f"  Raw DB type: {type(raw_value)}")
        
        print("\n" + "="*70)
        print("COMPARISON")
        print("="*70)
        print(f"Current UTC time:     {now_utc}")
        print(f"Current naive time:   {now_naive}")
        
        for post in posts:
            scheduled_time = post.scheduled_send_at
            print(f"\nPost {post.id}:")
            print(f"  Scheduled: {scheduled_time}")
            
            # Compare with UTC
            if scheduled_time.tzinfo is None:
                scheduled_utc = scheduled_time.replace(tzinfo=timezone.utc)
                print(f"  Scheduled (as UTC): {scheduled_utc}")
                print(f"  Comparison with UTC: {scheduled_utc} <= {now_utc} = {scheduled_utc <= now_utc}")
            else:
                print(f"  Comparison with UTC: {scheduled_time} <= {now_utc} = {scheduled_time <= now_utc}")

if __name__ == "__main__":
    asyncio.run(check_scheduled_posts())
