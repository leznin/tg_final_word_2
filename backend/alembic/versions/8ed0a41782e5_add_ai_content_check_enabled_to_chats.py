"""add_ai_content_check_enabled_to_chats

Revision ID: 8ed0a41782e5
Revises: 8fcb0d9d50db
Create Date: 2025-09-29 16:56:39.462038

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8ed0a41782e5'
down_revision: Union[str, Sequence[str], None] = '8fcb0d9d50db'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add ai_content_check_enabled column to chats table
    op.add_column('chats', sa.Column('ai_content_check_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove ai_content_check_enabled column from chats table
    op.drop_column('chats', 'ai_content_check_enabled')
