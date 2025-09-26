"""fix_chat_members_id_type

Revision ID: 6107ecf2e879
Revises: 814d4c00d5e4
Create Date: 2025-09-25 22:34:52.925643

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6107ecf2e879'
down_revision: Union[str, Sequence[str], None] = '814d4c00d5e4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
