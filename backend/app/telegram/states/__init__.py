"""
States for Telegram bot FSM (Finite State Machine)
"""

from aiogram.fsm.state import State, StatesGroup


class ChatManagementStates(StatesGroup):
    """States for chat management and channel linking"""

    # User is selecting a chat to manage
    selecting_chat = State()

    # User is waiting for forwarded message from channel to link it
    waiting_for_channel_forward = State()

    # User is confirming channel unlinking
    confirming_unlink = State()

    # User is setting message edit timeout for a chat
    setting_edit_timeout = State()

    # User is waiting for custom timeout value input
    waiting_for_custom_timeout = State()