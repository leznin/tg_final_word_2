"""add_member_status_and_left_at_to_chat_members

Revision ID: e7b712d9d9a0
Revises: 71594d7cbb4a
Create Date: 2025-10-21 18:54:44.162751

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e7b712d9d9a0'
down_revision: Union[str, Sequence[str], None] = '71594d7cbb4a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add new columns to chat_members table
    op.add_column('chat_members', sa.Column('status', sa.String(length=20), nullable=True, default='active'))
    op.add_column('chat_members', sa.Column('left_at', sa.DateTime(timezone=True), nullable=True))

    # Set default status for existing records
    op.execute("UPDATE chat_members SET status = 'active' WHERE status IS NULL")

    # Make status NOT NULL
    op.alter_column('chat_members', 'status', nullable=False, default='active')


def downgrade() -> None:
    """Downgrade schema."""
    # Remove the new columns
    op.drop_column('chat_members', 'status')
    op.drop_column('chat_members', 'left_at')
