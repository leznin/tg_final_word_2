"""add_notify_on_user_changes_to_chats

Revision ID: 28933715f49c
Revises: 6074da8417f4
Create Date: 2025-11-08 16:51:08.738190

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '28933715f49c'
down_revision: Union[str, Sequence[str], None] = '6074da8417f4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add notify_on_user_changes column to chats table with default value True
    op.add_column('chats', sa.Column('notify_on_user_changes', sa.Boolean(), nullable=False, server_default=sa.text('true')))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove notify_on_user_changes column from chats table
    op.drop_column('chats', 'notify_on_user_changes')
