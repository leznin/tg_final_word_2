"""add_purchased_by_user_id_to_chat_subscriptions

Revision ID: 1d3ad8a9365c
Revises: e3686c017ed7
Create Date: 2025-09-30 15:42:35.093637

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d3ad8a9365c'
down_revision: Union[str, Sequence[str], None] = 'e3686c017ed7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
