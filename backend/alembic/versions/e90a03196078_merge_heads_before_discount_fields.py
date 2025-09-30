"""merge_heads_before_discount_fields

Revision ID: e90a03196078
Revises: d4f8c9a1b2e3, afbb02478d7c
Create Date: 2025-09-30 14:31:34.815160

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e90a03196078'
down_revision: Union[str, Sequence[str], None] = ('d4f8c9a1b2e3', 'afbb02478d7c')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
