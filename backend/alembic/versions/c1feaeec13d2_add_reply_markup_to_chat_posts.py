"""add_reply_markup_to_chat_posts

Revision ID: c1feaeec13d2
Revises: 9a8695f1d7c9
Create Date: 2025-11-06 12:10:23.782725

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1feaeec13d2'
down_revision: Union[str, Sequence[str], None] = '9a8695f1d7c9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add reply_markup column to chat_posts table
    op.add_column('chat_posts', sa.Column('reply_markup', sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove reply_markup column from chat_posts table
    op.drop_column('chat_posts', 'reply_markup')
