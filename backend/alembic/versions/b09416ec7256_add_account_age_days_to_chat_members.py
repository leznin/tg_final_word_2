"""add_account_age_days_to_chat_members

Revision ID: b09416ec7256
Revises: ab463731fa55
Create Date: 2025-10-02 13:41:00.771276

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b09416ec7256'
down_revision: Union[str, Sequence[str], None] = 'ab463731fa55'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
