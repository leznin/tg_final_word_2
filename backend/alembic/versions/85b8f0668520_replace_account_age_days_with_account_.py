"""replace_account_age_days_with_account_creation_date

Revision ID: 85b8f0668520
Revises: b09416ec7256
Create Date: 2025-10-02 14:22:16.533958

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '85b8f0668520'
down_revision: Union[str, Sequence[str], None] = 'b09416ec7256'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
