"""fix_telegram_user_id_column_type_in_user_search_logs

Revision ID: 6074da8417f4
Revises: e24501900f6a
Create Date: 2025-11-08 16:30:24.633924

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6074da8417f4'
down_revision: Union[str, Sequence[str], None] = 'e24501900f6a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Change telegram_user_id from Integer to BigInteger
    op.alter_column('user_search_logs', 'telegram_user_id',
                    existing_type=sa.Integer(),
                    type_=sa.BigInteger(),
                    existing_nullable=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Revert telegram_user_id from BigInteger back to Integer
    op.alter_column('user_search_logs', 'telegram_user_id',
                    existing_type=sa.BigInteger(),
                    type_=sa.Integer(),
                    existing_nullable=False)
