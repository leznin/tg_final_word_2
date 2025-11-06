"""
Comprehensive check of chat posts scheduling system
"""
import asyncio
from datetime import datetime, timezone
from sqlalchemy import select, and_
from app.core.database import async_session
from app.models.chat_posts import ChatPost


async def check_all_posts():
    """Check all posts in the system"""
    async with async_session() as db:
        now = datetime.now(timezone.utc)
        print(f"Current time (UTC): {now}")
        print("=" * 80)
        
        # Get all non-deleted posts
        query = select(ChatPost).where(ChatPost.is_deleted == False)
        result = await db.execute(query)
        posts = result.scalars().all()
        
        if not posts:
            print("No posts found in the database.")
            return
        
        print(f"\n📊 Total posts: {len(posts)}\n")
        
        # Categorize posts
        pinned_posts = [p for p in posts if p.is_pinned]
        scheduled_unpin_posts = [p for p in posts if p.scheduled_unpin_at is not None]
        ready_to_unpin = [p for p in posts if p.scheduled_unpin_at and p.scheduled_unpin_at <= now and p.is_pinned]
        scheduled_send_posts = [p for p in posts if not p.is_sent and p.scheduled_send_at]
        ready_to_send = [p for p in posts if not p.is_sent and p.scheduled_send_at and p.scheduled_send_at <= now]
        
        print(f"📌 Pinned posts: {len(pinned_posts)}")
        print(f"⏰ Posts with scheduled unpin: {len(scheduled_unpin_posts)}")
        print(f"✅ Posts ready to unpin NOW: {len(ready_to_unpin)}")
        print(f"📅 Posts scheduled to send: {len(scheduled_send_posts)}")
        print(f"🚀 Posts ready to send NOW: {len(ready_to_send)}")
        print("=" * 80)
        
        # Show details of posts with scheduled unpin
        if scheduled_unpin_posts:
            print("\n📋 Posts with scheduled unpin time:")
            print("-" * 80)
            for post in scheduled_unpin_posts:
                time_until_unpin = post.scheduled_unpin_at - now
                is_ready = post.scheduled_unpin_at <= now
                
                status = "✅ READY" if is_ready else "⏳ WAITING"
                pin_status = "📌 PINNED" if post.is_pinned else "📍 UNPINNED"
                
                print(f"\n{status} | {pin_status} | Post ID: {post.id}")
                print(f"  Chat ID: {post.chat_id}")
                print(f"  Message ID: {post.telegram_message_id}")
                print(f"  Content: {(post.content_text[:60] + '...') if post.content_text and len(post.content_text) > 60 else post.content_text}")
                print(f"  Sent at: {post.sent_at}")
                print(f"  Scheduled unpin: {post.scheduled_unpin_at}")
                print(f"  Pin duration: {post.pin_duration_minutes} min")
                
                if is_ready:
                    print(f"  ⚠️  OVERDUE by: {-time_until_unpin}")
                else:
                    print(f"  ⏰ Time until unpin: {time_until_unpin}")
        
        # Show details of ready to unpin
        if ready_to_unpin:
            print("\n\n🚨 ATTENTION: These posts should be unpinned NOW:")
            print("-" * 80)
            for post in ready_to_unpin:
                print(f"  Post ID {post.id} in Chat {post.chat_id}")
                print(f"    Was scheduled for: {post.scheduled_unpin_at}")
                print(f"    Overdue by: {now - post.scheduled_unpin_at}")
        
        # Show recent posts
        print("\n\n📝 5 Most recent posts:")
        print("-" * 80)
        recent = sorted(posts, key=lambda p: p.created_at, reverse=True)[:5]
        for post in recent:
            send_status = "✅ Sent" if post.is_sent else "⏳ Scheduled"
            pin_status = "📌 Pinned" if post.is_pinned else ""
            print(f"{send_status} {pin_status} | ID: {post.id} | Chat: {post.chat_id} | Created: {post.created_at}")


async def main():
    print("🔍 Checking Chat Posts Scheduling System")
    print("=" * 80)
    await check_all_posts()
    print("\n" + "=" * 80)
    print("\n💡 To enable debug logging, uncomment the line in process_scheduled_actions()")
    print("   File: backend/app/services/chat_posts.py, line ~472")


if __name__ == "__main__":
    asyncio.run(main())
