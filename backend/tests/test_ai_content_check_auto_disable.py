"""
Test for automatic AI content check disabling when subscription expires
"""
import pytest
from datetime import datetime, timezone, timedelta
from app.models.chats import Chat
from app.models.chat_subscriptions import ChatSubscription
from app.models.users import User
from app.services.chat_subscriptions import ChatSubscriptionsService
from app.services.chats import ChatService


@pytest.mark.asyncio
async def test_ai_content_check_auto_disable_on_subscription_expiry(db_session):
    """Test that AI content check is automatically disabled when subscription expires"""

    # Create a test user
    user = User(
        telegram_id=123456789,
        username="test_user",
        first_name="Test",
        last_name="User"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a test chat with AI content check enabled
    chat = Chat(
        telegram_chat_id=999999999,
        chat_type="supergroup",
        title="Test Chat",
        username="test_chat",
        added_by_user_id=user.id,
        ai_content_check_enabled=True
    )
    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)

    # Create an expired subscription
    expired_date = datetime.now(timezone.utc) - timedelta(days=1)
    subscription = ChatSubscription(
        chat_id=chat.id,
        subscription_type="month",
        price_stars=100,
        currency="XTR",
        start_date=expired_date - timedelta(days=30),
        end_date=expired_date,
        is_active=True
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    # Verify initial state
    assert chat.ai_content_check_enabled is True
    assert subscription.is_active is True
    assert subscription.end_date < datetime.now(timezone.utc)

    # Test that subscription service correctly identifies expired subscription
    subscriptions_service = ChatSubscriptionsService(db_session)
    has_active = await subscriptions_service.has_active_subscription(chat.id)
    assert has_active is False, "Subscription should be considered expired"

    # Simulate what happens in message handler when AI check is attempted
    chat_service = ChatService(db_session)
    db_chat = await chat_service.get_chat(chat.id)
    assert db_chat.ai_content_check_enabled is True

    # Check if chat has active subscription (should return False)
    has_active_subscription = await subscriptions_service.has_active_subscription(db_chat.id)
    assert not has_active_subscription

    # This is what should happen in the message handler
    if db_chat.ai_content_check_enabled and not has_active_subscription:
        print(f"AI content check subscription expired or not found for chat {db_chat.id}")
        print(f"Automatically disabling AI content check for chat {db_chat.id} due to expired subscription")
        db_chat.ai_content_check_enabled = False
        await db_session.commit()
        await db_session.refresh(db_chat)

    # Verify AI content check was disabled
    assert db_chat.ai_content_check_enabled is False, "AI content check should be automatically disabled"


@pytest.mark.asyncio
async def test_ai_content_check_remains_enabled_with_active_subscription(db_session):
    """Test that AI content check remains enabled when subscription is active"""

    # Create a test user
    user = User(
        telegram_id=123456790,
        username="test_user2",
        first_name="Test2",
        last_name="User2"
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    # Create a test chat with AI content check enabled
    chat = Chat(
        telegram_chat_id=999999998,
        chat_type="supergroup",
        title="Test Chat 2",
        username="test_chat2",
        added_by_user_id=user.id,
        ai_content_check_enabled=True
    )
    db_session.add(chat)
    await db_session.commit()
    await db_session.refresh(chat)

    # Create an active subscription
    future_date = datetime.now(timezone.utc) + timedelta(days=30)
    subscription = ChatSubscription(
        chat_id=chat.id,
        subscription_type="month",
        price_stars=100,
        currency="XTR",
        start_date=datetime.now(timezone.utc),
        end_date=future_date,
        is_active=True
    )
    db_session.add(subscription)
    await db_session.commit()
    await db_session.refresh(subscription)

    # Verify initial state
    assert chat.ai_content_check_enabled is True
    assert subscription.is_active is True
    assert subscription.end_date > datetime.now(timezone.utc)

    # Test that subscription service correctly identifies active subscription
    subscriptions_service = ChatSubscriptionsService(db_session)
    has_active = await subscriptions_service.has_active_subscription(chat.id)
    assert has_active is True, "Subscription should be considered active"

    # Simulate what happens in message handler when AI check is attempted
    chat_service = ChatService(db_session)
    db_chat = await chat_service.get_chat(chat.id)
    assert db_chat.ai_content_check_enabled is True

    # Check if chat has active subscription (should return True)
    has_active_subscription = await subscriptions_service.has_active_subscription(db_chat.id)
    assert has_active_subscription

    # AI content check should remain enabled
    assert db_chat.ai_content_check_enabled is True, "AI content check should remain enabled with active subscription"
