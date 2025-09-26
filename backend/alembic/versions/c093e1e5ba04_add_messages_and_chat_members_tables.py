"""add_messages_and_chat_members_tables

Revision ID: c093e1e5ba04
Revises: 4922b0cb1e22
Create Date: 2025-09-25 22:14:18.503243

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c093e1e5ba04'
down_revision: Union[str, Sequence[str], None] = '4922b0cb1e22'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
