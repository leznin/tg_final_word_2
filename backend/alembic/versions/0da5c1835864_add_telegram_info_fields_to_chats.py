"""add_telegram_info_fields_to_chats

Revision ID: 0da5c1835864
Revises: b241aa62ce20
Create Date: 2025-09-28 10:49:50.941507

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0da5c1835864'
down_revision: Union[str, Sequence[str], None] = 'b241aa62ce20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns for Telegram API information
    op.add_column('chats', sa.Column('member_count', sa.Integer(), nullable=True))
    op.add_column('chats', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('chats', sa.Column('invite_link', sa.String(length=255), nullable=True))
    op.add_column('chats', sa.Column('bot_permissions', sa.JSON(), nullable=True))
    op.add_column('chats', sa.Column('last_info_update', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove new columns
    op.drop_column('chats', 'last_info_update')
    op.drop_column('chats', 'bot_permissions')
    op.drop_column('chats', 'invite_link')
    op.drop_column('chats', 'description')
    op.drop_column('chats', 'member_count')
