"""add_account_ages_table

Revision ID: ab463731fa55
Revises: 1d3ad8a9365c
Create Date: 2025-10-02 13:35:31.717574

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ab463731fa55'
down_revision: Union[str, Sequence[str], None] = '1d3ad8a9365c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
