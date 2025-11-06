"""add chat_posts table

Revision ID: add_chat_posts_001
Revises: a35560e6926e
Create Date: 2025-11-06

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = 'add_chat_posts_001'
down_revision = 'a35560e6926e'  # Previous migration
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create chat_posts table"""
    op.create_table(
        'chat_posts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('telegram_message_id', sa.BigInteger(), nullable=True),
        sa.Column('scheduled_send_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('content_text', sa.Text(), nullable=True),
        sa.Column('media_type', sa.String(length=50), nullable=True),
        sa.Column('media_file_id', sa.String(length=255), nullable=True),
        sa.Column('media_url', sa.String(length=500), nullable=True),
        sa.Column('media_filename', sa.String(length=255), nullable=True),
        sa.Column('is_pinned', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('pin_duration_minutes', sa.Integer(), nullable=True),
        sa.Column('scheduled_unpin_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('delete_after_minutes', sa.Integer(), nullable=True),
        sa.Column('scheduled_delete_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by_user_id', sa.Integer(), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['created_by_user_id'], ['admin_users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('ix_chat_posts_id', 'chat_posts', ['id'])
    op.create_index('ix_chat_posts_chat_id', 'chat_posts', ['chat_id'])
    op.create_index('ix_chat_posts_telegram_message_id', 'chat_posts', ['telegram_message_id'])
    op.create_index('ix_chat_posts_scheduled_send_at', 'chat_posts', ['scheduled_send_at'])
    op.create_index('ix_chat_posts_scheduled_unpin_at', 'chat_posts', ['scheduled_unpin_at'])
    op.create_index('ix_chat_posts_scheduled_delete_at', 'chat_posts', ['scheduled_delete_at'])


def downgrade() -> None:
    """Drop chat_posts table"""
    op.drop_index('ix_chat_posts_scheduled_delete_at', table_name='chat_posts')
    op.drop_index('ix_chat_posts_scheduled_unpin_at', table_name='chat_posts')
    op.drop_index('ix_chat_posts_scheduled_send_at', table_name='chat_posts')
    op.drop_index('ix_chat_posts_telegram_message_id', table_name='chat_posts')
    op.drop_index('ix_chat_posts_chat_id', table_name='chat_posts')
    op.drop_index('ix_chat_posts_id', table_name='chat_posts')
    op.drop_table('chat_posts')
