"""add_discount_fields_to_subscription_prices

Revision ID: e3686c017ed7
Revises: e90a03196078
Create Date: 2025-09-30 14:31:36.542974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e3686c017ed7'
down_revision: Union[str, Sequence[str], None] = 'e90a03196078'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
