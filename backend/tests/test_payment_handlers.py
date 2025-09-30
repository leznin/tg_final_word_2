"""
Test payment handlers
"""
import pytest
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, SuccessfulPayment, User
from app.telegram.handlers.payments import success_payment_handler
from app.models.chat_subscriptions import ChatSubscription


@pytest.mark.asyncio
async def test_success_payment_handler(db_session):
    """Test successful payment handler creates subscription"""

    # Mock message with successful payment
    mock_payment = SuccessfulPayment(
        currency="XTR",
        total_amount=20,
        invoice_payload="month:1:123456789",
        telegram_payment_charge_id="test_charge_id",
        provider_payment_charge_id="provider_id"
    )

    mock_user = User(id=123456789, is_bot=False, first_name="Test User")

    mock_message = Message(
        message_id=1,
        date=None,
        chat=None,
        from_user=mock_user,
        successful_payment=mock_payment
    )

    # Mock bot
    mock_bot = AsyncMock()

    # Call handler
    await success_payment_handler(mock_message, db_session, mock_bot)

    # Check that subscription was created
    result = await db_session.execute(
        f"SELECT * FROM chat_subscriptions WHERE telegram_payment_charge_id = 'test_charge_id'"
    )
    subscription = result.fetchone()

    assert subscription is not None
    assert subscription.subscription_type == "month"
    assert subscription.price_stars == 20
    assert subscription.chat_id == 1
    print("✅ Payment handler test passed - subscription created")


@pytest.mark.asyncio
async def test_success_payment_handler_invalid_payload(db_session):
    """Test successful payment handler with invalid payload"""

    # Mock message with invalid payload
    mock_payment = SuccessfulPayment(
        currency="XTR",
        total_amount=20,
        invoice_payload="invalid_payload",
        telegram_payment_charge_id="test_charge_id_2",
        provider_payment_charge_id="provider_id"
    )

    mock_user = User(id=123456789, is_bot=False, first_name="Test User")

    mock_message = Message(
        message_id=1,
        date=None,
        chat=None,
        from_user=mock_user,
        successful_payment=mock_payment
    )

    # Mock bot
    mock_bot = AsyncMock()

    # Call handler - should handle error gracefully
    await success_payment_handler(mock_message, db_session, mock_bot)

    # Should not create subscription with invalid payload
    result = await db_session.execute(
        f"SELECT * FROM chat_subscriptions WHERE telegram_payment_charge_id = 'test_charge_id_2'"
    )
    subscription = result.fetchone()

    assert subscription is None
    print("✅ Invalid payload test passed - no subscription created")
