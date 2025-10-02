"""add_account_creation_date_to_chat_members

Revision ID: b0f163137fda
Revises: 85b8f0668520
Create Date: 2025-10-02 14:26:12.815069

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b0f163137fda'
down_revision: Union[str, Sequence[str], None] = '85b8f0668520'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add account_creation_date column to chat_members table
    op.add_column('chat_members', sa.Column('account_creation_date', sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove account_creation_date column from chat_members table
    op.drop_column('chat_members', 'account_creation_date')
