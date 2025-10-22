"""
Chat member updates handler for tracking user joins, leaves, bans, and kicks
"""

from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.chats import ChatService
from app.services.chat_members import ChatMemberService
from app.services.telegram_users import TelegramUserService
from app.schemas.telegram_users import TelegramUserData
from app.utils.account_age import get_account_creation_date

# Create router for chat member updates
chat_member_router = Router()


def get_member_status_change(old_status: str, new_status: str) -> str:
    """
    Determine the type of status change
    Returns: 'joined', 'left', 'banned', 'kicked', 'unbanned', 'unkicked', 'unknown'
    """
    # Member joined the chat
    if old_status in ['left', 'banned', 'kicked'] and new_status in ['member', 'administrator', 'creator']:
        return 'joined'

    # Member left voluntarily
    if old_status in ['member', 'administrator', 'creator'] and new_status == 'left':
        return 'left'

    # Member was banned
    if old_status != 'banned' and new_status == 'banned':
        return 'banned'

    # Member was unbanned
    if old_status == 'banned' and new_status != 'banned':
        return 'unbanned'

    # Member was kicked/restricted
    if old_status in ['member', 'administrator', 'creator'] and new_status in ['restricted', 'kicked']:
        return 'kicked'

    # Member restrictions were lifted
    if old_status in ['restricted', 'kicked'] and new_status in ['member', 'administrator', 'creator']:
        return 'unkicked'

    return 'unknown'


@chat_member_router.chat_member()
async def handle_chat_member_update(update: types.ChatMemberUpdated, db: AsyncSession) -> None:
    """
    Handle chat member status changes (joins, leaves, bans, kicks)
    """
    # Only process updates from group chats
    if update.chat.type not in ['group', 'supergroup']:
        return

    chat_service = ChatService(db)
    member_service = ChatMemberService(db)
    telegram_user_service = TelegramUserService(db)

    # Get the chat from database
    chat = await chat_service.get_chat_by_telegram_id(update.chat.id)
    if not chat:
        print(f"Chat {update.chat.id} not found in database")
        return

    # Extract user information
    user = update.new_chat_member.user
    account_creation_date = await get_account_creation_date(user.id)
    telegram_user_data = TelegramUserData(
        telegram_user_id=user.id,
        is_bot=user.is_bot,
        first_name=user.first_name,
        last_name=user.last_name,
        username=user.username,
        language_code=user.language_code,
        is_premium=getattr(user, 'is_premium', None),
        added_to_attachment_menu=getattr(user, 'added_to_attachment_menu', None),
        can_join_groups=getattr(user, 'can_join_groups', None),
        can_read_all_group_messages=getattr(user, 'can_read_all_group_messages', None),
        supports_inline_queries=getattr(user, 'supports_inline_queries', None),
        can_connect_to_business=getattr(user, 'can_connect_to_business', None),
        has_main_web_app=getattr(user, 'has_main_web_app', None),
        account_creation_date=account_creation_date
    )

    # Create or update telegram user
    await telegram_user_service.create_or_update_user_from_telegram(telegram_user_data)

    # Determine the status change
    old_status = update.old_chat_member.status
    new_status = update.new_chat_member.status

    status_change = get_member_status_change(old_status, new_status)

    print(f"Chat member update: User {user.id} ({user.full_name}) in chat {chat.id}")
    print(f"  Status change: {old_status} -> {new_status} ({status_change})")

    if status_change == 'joined':
        # User joined the chat
        await member_service.create_or_update_member_from_telegram(chat.id, telegram_user_data)
        print(f"  ✅ User {user.id} joined chat {chat.id}")

    elif status_change in ['left', 'banned', 'kicked']:
        # User left, was banned, or kicked
        success = await member_service.remove_member_from_chat(
            chat_id=chat.id,
            telegram_user_id=user.id,
            reason=status_change
        )
        if success:
            print(f"  ✅ User {user.id} {status_change} from chat {chat.id}")
        else:
            print(f"  ⚠️  Failed to update status for user {user.id} in chat {chat.id}")

    elif status_change in ['unbanned', 'unkicked']:
        # User was unbanned or restrictions lifted - reactivate membership
        member = await member_service.update_member_status(
            chat_id=chat.id,
            telegram_user_id=user.id,
            status='active'
        )
        if member:
            member.left_at = None  # Clear the left timestamp
            await db.commit()
            print(f"  ✅ User {user.id} reactivated in chat {chat.id}")
        else:
            print(f"  ⚠️  Failed to reactivate user {user.id} in chat {chat.id}")

    else:
        print(f"  ℹ️  Unknown status change for user {user.id}: {old_status} -> {new_status}")


@chat_member_router.my_chat_member()
async def handle_my_chat_member_update(update: types.ChatMemberUpdated, db: AsyncSession) -> None:
    """
    Handle bot's own membership status changes
    """
    print(f"Bot membership update in chat {update.chat.id}: {update.old_chat_member.status} -> {update.new_chat_member.status}")

    # This is mainly for logging - bot membership changes are handled elsewhere
    # in the chat management system
