"""fix_telegram_message_id_nullable

Revision ID: 9a8695f1d7c9
Revises: add_chat_posts_001
Create Date: 2025-11-06 11:26:48.161032

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a8695f1d7c9'
down_revision: Union[str, Sequence[str], None] = 'add_chat_posts_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make telegram_message_id nullable."""
    # For MySQL, we need to explicitly alter the column to allow NULL
    op.alter_column('chat_posts', 'telegram_message_id',
                    existing_type=sa.BigInteger(),
                    nullable=True)


def downgrade() -> None:
    """Make telegram_message_id not nullable."""
    # Downgrade by making it NOT NULL again (if needed)
    op.alter_column('chat_posts', 'telegram_message_id',
                    existing_type=sa.BigInteger(),
                    nullable=False)
