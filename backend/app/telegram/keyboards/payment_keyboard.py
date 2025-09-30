"""
Payment keyboards for Telegram Stars payments
"""

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def payment_keyboard(price_stars: int, subscription_type: str, chat_id: int) -> InlineKeyboardMarkup:
    """
    Create payment keyboard for AI content check subscription

    According to aiogram documentation, for Telegram Stars we need to provide
    a keyboard with pay=True button.

    Args:
        price_stars: Price in Telegram Stars
        subscription_type: Type of subscription ('month' or 'year')
        chat_id: Chat ID for which subscription is purchased

    Returns:
        InlineKeyboardMarkup: Payment keyboard with pay button
    """
    builder = InlineKeyboardBuilder()

    subscription_text = "месяц" if subscription_type == "month" else "год"
    button_text = f"Оплатить {price_stars} ⭐️ ({subscription_text})"

    builder.button(text=button_text, pay=True)

    return builder.as_markup()


def payment_options_keyboard(chat_id: int, prices: dict) -> InlineKeyboardMarkup:
    """
    Create keyboard with payment options for different subscription types

    Args:
        chat_id: Chat ID for which subscription is purchased
        prices: Dictionary with subscription types and their prices
               Format: {'month': 10, 'year': 100}

    Returns:
        InlineKeyboardMarkup: Payment options keyboard
    """
    builder = InlineKeyboardBuilder()

    # Add buttons for each subscription type
    for subscription_type, price_stars in prices.items():
        subscription_text = "месяц" if subscription_type == "month" else "год"
        button_text = f"Оплатить {price_stars} ⭐️ ({subscription_text})"

        # Note: aiogram only supports one pay button per keyboard
        # So we'll use callback buttons that lead to invoice creation
        callback_data = f"pay_ai:{subscription_type}:{chat_id}"
        builder.button(text=button_text, callback_data=callback_data)

    builder.adjust(1)  # One button per row

    return builder.as_markup()


def cancel_payment_keyboard() -> InlineKeyboardMarkup:
    """
    Create keyboard with cancel payment button

    Returns:
        InlineKeyboardMarkup: Cancel keyboard
    """
    builder = InlineKeyboardBuilder()
    builder.button(text="❌ Отмена", callback_data="cancel_payment")

    return builder.as_markup()
