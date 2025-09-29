"""remove_bot_permissions_and_last_info_update_from_chats

Revision ID: b2f5bd880aa5
Revises: 8ed0a41782e5
Create Date: 2025-09-29 17:08:43.019116

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2f5bd880aa5'
down_revision: Union[str, Sequence[str], None] = '8ed0a41782e5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
