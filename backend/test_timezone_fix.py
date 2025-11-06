"""
Test creating a scheduled post to verify timezone conversion
"""

import asyncio
from datetime import datetime, timedelta, timezone
from app.core.database import async_session
from app.services.chat_posts import ChatPostService
from aiogram import Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from app.core.config import settings
from app.schemas.chat_posts import ChatPostCreate
from sqlalchemy import select, text
from app.models.chats import Chat
from app.models.chat_posts import ChatPost

# Test chat ID
TEST_CHAT_TELEGRAM_ID = -1003062613079


async def test_timezone_conversion():
    """Test timezone conversion in scheduled posts"""
    print("="*70)
    print("TIMEZONE CONVERSION TEST")
    print("="*70)
    
    async with async_session() as db:
        # Get test chat
        result = await db.execute(
            select(Chat).where(Chat.telegram_chat_id == TEST_CHAT_TELEGRAM_ID)
        )
        chat = result.scalar_one_or_none()
        
        if not chat:
            print(f"❌ Chat with telegram_chat_id {TEST_CHAT_TELEGRAM_ID} not found")
            return
        
        print(f"✅ Found chat: {chat.title} (ID: {chat.id})\n")
        
        # Create bot instance
        bot = Bot(
            token=settings.TELEGRAM_BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        # Create service
        service = ChatPostService(db, bot)
        
        # Test 1: Schedule post 2 minutes from now with explicit timezone (GMT+4)
        print("Test 1: Creating scheduled post with GMT+4 timezone")
        print("-" * 70)
        
        # Simulate what frontend sends: local time with timezone
        from datetime import timezone as tz
        local_tz = tz(timedelta(hours=4))  # GMT+4
        local_time = datetime.now(local_tz) + timedelta(minutes=2)
        
        print(f"Local time (GMT+4): {local_time}")
        print(f"Expected UTC time:  {local_time.astimezone(timezone.utc)}")
        print(f"Current UTC time:   {datetime.now(timezone.utc)}")
        print()
        
        post_data = ChatPostCreate(
            chat_id=chat.id,
            content_text=f"🧪 Timezone Test: Created at {datetime.now(local_tz).strftime('%H:%M:%S %Z')}\nScheduled for 2 minutes from now",
            send_immediately=False,
            scheduled_send_at=local_time
        )
        
        try:
            post = await service.create_post(post_data, created_by_user_id=1)
            print(f"✅ Post created successfully!")
            print(f"   Post ID: {post.id}")
            print(f"   Scheduled send at: {post.scheduled_send_at}")
            print(f"   Timezone info: {post.scheduled_send_at.tzinfo}")
            
            # Check raw database value
            raw_query = text(f"SELECT scheduled_send_at FROM chat_posts WHERE id = {post.id}")
            raw_result = await db.execute(raw_query)
            raw_value = raw_result.scalar()
            print(f"   Raw DB value: {raw_value}")
            print(f"   Raw DB type: {type(raw_value)}")
            
            # Verify the time is stored correctly
            expected_utc = local_time.astimezone(timezone.utc)
            stored_time = post.scheduled_send_at
            
            # Make stored time timezone-aware if needed for comparison
            if stored_time.tzinfo is None:
                stored_time = stored_time.replace(tzinfo=timezone.utc)
            
            print(f"\nVerification:")
            print(f"   Expected UTC: {expected_utc}")
            print(f"   Stored time:  {stored_time}")
            print(f"   Match: {abs((expected_utc - stored_time).total_seconds()) < 1}")
            
            return post.id
            
        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


async def check_post_will_send(post_id: int):
    """Check if the post will be sent by the scheduler"""
    print("\n" + "="*70)
    print("CHECKING IF POST WILL BE SENT")
    print("="*70)
    
    async with async_session() as db:
        result = await db.execute(
            select(ChatPost).where(ChatPost.id == post_id)
        )
        post = result.scalar_one_or_none()
        
        if not post:
            print(f"❌ Post {post_id} not found")
            return
        
        now_utc = datetime.now(timezone.utc)
        scheduled_time = post.scheduled_send_at
        
        # Make timezone-aware if needed
        if scheduled_time.tzinfo is None:
            scheduled_time = scheduled_time.replace(tzinfo=timezone.utc)
        
        print(f"Post ID: {post.id}")
        print(f"Current UTC time:    {now_utc}")
        print(f"Scheduled send time: {scheduled_time}")
        print(f"Time difference:     {(scheduled_time - now_utc).total_seconds()} seconds")
        print(f"Should send now:     {scheduled_time <= now_utc}")
        print(f"Will send in ~{int((scheduled_time - now_utc).total_seconds())} seconds")


async def main():
    """Main test function"""
    post_id = await test_timezone_conversion()
    
    if post_id:
        await check_post_will_send(post_id)
        print("\n" + "="*70)
        print("Wait 2 minutes and run: python test_send_now.py")
        print("Or the background task will send it automatically")
        print("="*70)


if __name__ == "__main__":
    asyncio.run(main())
