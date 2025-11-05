"""merge_multiple_heads

Revision ID: 9952f62943fb
Revises: 6dec0c237b1a, add_verification_schedule, f1a2b3c4d5e6
Create Date: 2025-11-05 18:21:09.613780

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9952f62943fb'
down_revision: Union[str, Sequence[str], None] = ('6dec0c237b1a', 'add_verification_schedule', 'f1a2b3c4d5e6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
