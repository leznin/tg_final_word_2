"""add_welcome_message_fields_to_chats

Revision ID: cb6178072e4b
Revises: c1feaeec13d2
Create Date: 2025-11-07 12:42:36.543960

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cb6178072e4b'
down_revision: Union[str, Sequence[str], None] = 'c1feaeec13d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add welcome message fields to chats table
    op.add_column('chats', sa.Column('welcome_message_enabled', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('chats', sa.Column('welcome_message_text', sa.Text(), nullable=True))
    op.add_column('chats', sa.Column('welcome_message_media_type', sa.String(20), nullable=True))
    op.add_column('chats', sa.Column('welcome_message_media_url', sa.String(255), nullable=True))
    op.add_column('chats', sa.Column('welcome_message_lifetime_minutes', sa.Integer(), nullable=True))
    op.add_column('chats', sa.Column('welcome_message_buttons', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove welcome message fields from chats table
    op.drop_column('chats', 'welcome_message_buttons')
    op.drop_column('chats', 'welcome_message_lifetime_minutes')
    op.drop_column('chats', 'welcome_message_media_url')
    op.drop_column('chats', 'welcome_message_media_type')
    op.drop_column('chats', 'welcome_message_text')
    op.drop_column('chats', 'welcome_message_enabled')
