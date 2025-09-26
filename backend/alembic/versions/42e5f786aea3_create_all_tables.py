"""create_all_tables

Revision ID: 42e5f786aea3
Revises: c093e1e5ba04
Create Date: 2025-09-25 22:15:10.086752

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '42e5f786aea3'
down_revision: Union[str, Sequence[str], None] = 'c093e1e5ba04'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
