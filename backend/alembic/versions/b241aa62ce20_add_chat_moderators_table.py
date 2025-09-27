"""add_chat_moderators_table

Revision ID: b241aa62ce20
Revises: add_auth_attempts_001
Create Date: 2025-09-26 18:34:09.825704

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b241aa62ce20'
down_revision: Union[str, Sequence[str], None] = 'add_auth_attempts_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create chat_moderators table
    op.create_table('chat_moderators',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('moderator_user_id', sa.BigInteger(), nullable=False),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('added_by_user_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.ForeignKeyConstraint(['added_by_user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('chat_id', 'moderator_user_id', name='unique_chat_moderator')
    )

    # Create indexes for better performance
    op.create_index('ix_chat_moderators_chat_id', 'chat_moderators', ['chat_id'], unique=False)
    op.create_index('ix_chat_moderators_moderator_user_id', 'chat_moderators', ['moderator_user_id'], unique=False)
    op.create_index('ix_chat_moderators_added_by_user_id', 'chat_moderators', ['added_by_user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_chat_moderators_added_by_user_id', table_name='chat_moderators')
    op.drop_index('ix_chat_moderators_moderator_user_id', table_name='chat_moderators')
    op.drop_index('ix_chat_moderators_chat_id', table_name='chat_moderators')

    # Drop table
    op.drop_table('chat_moderators')
