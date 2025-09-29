"""add_delete_messages_enabled_to_chats

Revision ID: afbb02478d7c
Revises: b2f5bd880aa5
Create Date: 2025-09-29 17:26:49.912897

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afbb02478d7c'
down_revision: Union[str, Sequence[str], None] = 'b2f5bd880aa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add delete_messages_enabled column to chats table
    op.add_column('chats', sa.Column('delete_messages_enabled', sa.Boolean(), nullable=False, server_default=sa.text('false')))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove delete_messages_enabled column from chats table
    op.drop_column('chats', 'delete_messages_enabled')
