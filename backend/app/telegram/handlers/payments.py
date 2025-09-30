"""
Payment handlers for Telegram Stars payments
"""

from aiogram import Router, F, Bot
from aiogram.types import Message, PreCheckoutQuery, CallbackQuery, LabeledPrice
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.subscription_prices import SubscriptionPricesService
from app.services.chat_subscriptions import ChatSubscriptionsService
from app.services.chats import ChatService
from app.telegram.keyboards.payment_keyboard import payment_keyboard, payment_options_keyboard, cancel_payment_keyboard
from app.telegram.utils.constants import PaymentMessages

# Create router for payment handlers
payment_router = Router()


@payment_router.message(Command(commands=["test_pay"]))
async def test_payment_command(
    message: Message,
    db: AsyncSession,
    bot: Bot
) -> None:
    """
    Test command to create a payment invoice
    """
    try:
        # Get first available price
        prices_service = SubscriptionPricesService(db)
        price = await prices_service.get_price_by_type('month')

        if not price:
            await message.reply("❌ Цены подписок не настроены")
            return

        prices = [LabeledPrice(label="XTR", amount=price.price_stars)]
        payload = f"month:test:{message.from_user.id}"

        test_message = await bot.send_invoice(
            chat_id=message.chat.id,
            title="Тест AI проверки контента",
            description="Тестовая подписка на AI проверку контента",
            prices=prices,
            provider_token="",
            payload=payload,
            currency="XTR",
            reply_markup=payment_keyboard(price.price_stars, 'month', 0)
        )

        await message.reply("✅ Тестовый счет создан")

    except Exception as e:
        print(f"Error in test_payment_command: {e}")
        await message.reply(f"❌ Ошибка: {e}")


@payment_router.callback_query(F.data.startswith("pay_ai:"))
async def handle_payment_request(
    callback: CallbackQuery,
    db: AsyncSession,
    bot: Bot
) -> None:
    """
    Handle payment request for AI content check subscription
    """
    try:
        # Parse callback data: pay_ai:subscription_type:chat_id
        _, subscription_type, chat_id_str = callback.data.split(":", 2)
        chat_id = int(chat_id_str)

        # Get subscription price
        prices_service = SubscriptionPricesService(db)
        price = await prices_service.get_price_by_type(subscription_type)

        if not price:
            await callback.answer("❌ Ошибка: цена подписки не найдена")
            return

        # Get chat information
        chat_service = ChatService(db)
        chat = await chat_service.get_chat(chat_id)

        if not chat:
            await callback.answer("❌ Ошибка: чат не найден")
            return

        # Create invoice
        prices = [LabeledPrice(label="XTR", amount=price.price_stars)]

        subscription_text = "месяц" if subscription_type == "month" else "год"
        title = f"AI проверка контента - {subscription_text}"
        description = f"Подписка на AI проверку контента для чата '{chat.title or f'ID: {chat.telegram_chat_id}'}' на {subscription_text}"

        # Payload format: subscription_type:chat_id:user_id
        payload = f"{subscription_type}:{chat_id}:{callback.from_user.id}"

        # Send invoice as a separate message
        message = await bot.send_invoice(
            chat_id=callback.from_user.id,
            title=title,
            description=description,
            prices=prices,
            provider_token="",  # Empty string for Telegram Stars
            payload=payload,
            currency="XTR",
            reply_markup=payment_keyboard(price.price_stars, subscription_type, chat_id)
        )

        # Answer callback after invoice is sent
        await callback.answer()

        print(f"Invoice sent successfully, message_id: {message.message_id}")

    except Exception as e:
        print(f"Error in handle_payment_request: {e}")
        await callback.answer("❌ Произошла ошибка при создании платежа")


@payment_router.pre_checkout_query()
async def pre_checkout_handler(
    pre_checkout_query: PreCheckoutQuery,
    db: AsyncSession
) -> None:
    """
    Handle pre-checkout query (payment verification)
    """
    print(f"💳 PRE-CHECKOUT QUERY RECEIVED: {pre_checkout_query.invoice_payload}")
    print(f"💳 PRE-CHECKOUT QUERY DATA: user_id={pre_checkout_query.from_user.id}, total_amount={pre_checkout_query.total_amount}")
    try:
        # Parse payload: subscription_type:chat_id:user_id
        payload_parts = pre_checkout_query.invoice_payload.split(":")
        if len(payload_parts) != 3:
            await pre_checkout_query.answer(ok=False, error_message="Неверные данные платежа")
            return

        subscription_type, chat_id_str, user_id_str = payload_parts
        chat_id = int(chat_id_str)
        user_id = int(user_id_str)

        # Verify that chat exists
        chat_service = ChatService(db)
        chat = await chat_service.get_chat(chat_id)

        if not chat:
            await pre_checkout_query.answer(
                ok=False,
                error_message="Чат не найден"
            )
            return

        # Check if subscription already exists
        subscriptions_service = ChatSubscriptionsService(db)
        existing_subscription = await subscriptions_service.get_active_subscription_for_chat(chat_id)

        if existing_subscription:
            await pre_checkout_query.answer(
                ok=False,
                error_message="У этого чата уже есть активная подписка на AI проверку"
            )
            return

        # All checks passed
        await pre_checkout_query.answer(ok=True)

    except Exception as e:
        print(f"Error in pre_checkout_handler: {e}")
        await pre_checkout_query.answer(ok=False, error_message="Ошибка проверки платежа")


@payment_router.message(F.successful_payment)
async def success_payment_handler(
    message: Message,
    db: AsyncSession,
    bot: Bot
) -> None:
    """
    Handle successful payment
    """
    print(f"🎉 SUCCESSFUL PAYMENT RECEIVED: {message.successful_payment}")
    print(f"🎉 PAYMENT DATA: user_id={message.from_user.id}, chat_id={message.chat.id}, total_amount={message.successful_payment.total_amount}")
    try:
        # Parse payload: subscription_type:chat_id:user_id
        payload_parts = message.successful_payment.invoice_payload.split(":")
        if len(payload_parts) != 3:
            await message.reply("❌ Ошибка обработки платежа: неверные данные")
            return

        subscription_type, chat_id_str, user_id_str = payload_parts
        chat_id = int(chat_id_str)
        user_id = int(user_id_str)

        # Create subscription
        subscriptions_service = ChatSubscriptionsService(db)
        await subscriptions_service.create_subscription_from_payment(
            chat_id=chat_id,
            subscription_type=subscription_type,
            price_stars=message.successful_payment.total_amount,
            telegram_payment_charge_id=message.successful_payment.telegram_payment_charge_id
        )

        # Get chat information for confirmation message
        chat_service = ChatService(db)
        chat = await chat_service.get_chat(chat_id)

        subscription_text = "месяц" if subscription_type == "month" else "год"
        chat_title = chat.title or f"ID: {chat.telegram_chat_id}" if chat else "ваш чат"

        confirmation_message = PaymentMessages.PAYMENT_SUCCESS.format(
            subscription_text=subscription_text,
            chat_title=chat_title,
            stars=message.successful_payment.total_amount
        )

        await message.reply(confirmation_message)

        # Enable AI content check for the chat
        if chat and not chat.ai_content_check_enabled:
            from app.schemas.chats import ChatUpdate
            chat_update = ChatUpdate(ai_content_check_enabled=True)
            await chat_service.update_chat(chat_id, chat_update)

    except Exception as e:
        print(f"Error in success_payment_handler: {e}")
        await message.reply("❌ Произошла ошибка при обработке платежа")


@payment_router.callback_query(F.data == "cancel_payment")
async def cancel_payment_handler(callback: CallbackQuery) -> None:
    """
    Handle payment cancellation
    """
    await callback.message.delete()
    await callback.answer("Платеж отменен")
