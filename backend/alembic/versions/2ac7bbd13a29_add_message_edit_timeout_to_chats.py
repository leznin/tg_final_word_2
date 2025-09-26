"""add_message_edit_timeout_to_chats

Revision ID: 2ac7bbd13a29
Revises: 6107ecf2e879
Create Date: 2025-09-25 23:49:55.917527

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2ac7bbd13a29'
down_revision: Union[str, Sequence[str], None] = '6107ecf2e879'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add message_edit_timeout_minutes column to chats table
    op.add_column('chats', sa.Column('message_edit_timeout_minutes', sa.SmallInteger(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove message_edit_timeout_minutes column from chats table
    op.drop_column('chats', 'message_edit_timeout_minutes')
