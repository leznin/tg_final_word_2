"""add_messages_and_chat_members_tables

Revision ID: 814d4c00d5e4
Revises: 42e5f786aea3
Create Date: 2025-09-25 22:24:40.725193

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '814d4c00d5e4'
down_revision: Union[str, Sequence[str], None] = '42e5f786aea3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create chat_members table
    op.create_table('chat_members',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('is_bot', sa.Boolean(), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('language_code', sa.String(length=10), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=True),
        sa.Column('added_to_attachment_menu', sa.Boolean(), nullable=True),
        sa.Column('can_join_groups', sa.Boolean(), nullable=True),
        sa.Column('can_read_all_group_messages', sa.Boolean(), nullable=True),
        sa.Column('supports_inline_queries', sa.Boolean(), nullable=True),
        sa.Column('can_connect_to_business', sa.Boolean(), nullable=True),
        sa.Column('has_main_web_app', sa.Boolean(), nullable=True),
        sa.Column('joined_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id', 'telegram_user_id', name='unique_chat_member')
    )

    # Create messages table
    op.create_table('messages',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('telegram_message_id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=True),
        sa.Column('message_type', sa.String(length=50), nullable=False),
        sa.Column('text_content', sa.Text(), nullable=True),
        sa.Column('media_file_id', sa.String(length=255), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id', 'telegram_message_id', name='unique_chat_message')
    )

    # Create indexes for better performance
    op.create_index('ix_chat_members_chat_id', 'chat_members', ['chat_id'], unique=False)
    op.create_index('ix_chat_members_telegram_user_id', 'chat_members', ['telegram_user_id'], unique=False)
    op.create_index('ix_messages_chat_id', 'messages', ['chat_id'], unique=False)
    op.create_index('ix_messages_created_at', 'messages', ['created_at'], unique=False)
    op.create_index('ix_messages_telegram_user_id', 'messages', ['telegram_user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_messages_telegram_user_id', table_name='messages')
    op.drop_index('ix_messages_created_at', table_name='messages')
    op.drop_index('ix_messages_chat_id', table_name='messages')
    op.drop_index('ix_chat_members_telegram_user_id', table_name='chat_members')
    op.drop_index('ix_chat_members_chat_id', table_name='chat_members')

    # Drop tables
    op.drop_table('messages')
    op.drop_table('chat_members')
