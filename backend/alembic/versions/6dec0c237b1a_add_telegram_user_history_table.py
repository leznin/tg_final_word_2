"""add_telegram_user_history_table

Revision ID: 6dec0c237b1a
Revises: e7b712d9d9a0
Create Date: 2025-10-22 17:54:07.112308

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6dec0c237b1a'
down_revision: Union[str, Sequence[str], None] = 'e7b712d9d9a0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create telegram_user_history table
    op.create_table('telegram_user_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False, index=True),
        sa.Column('field_name', sa.String(length=50), nullable=False),
        sa.Column('old_value', sa.String(length=255), nullable=True),
        sa.Column('new_value', sa.String(length=255), nullable=True),
        sa.Column('changed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    # Create index for better performance
    op.create_index('ix_telegram_user_history_changed_at', 'telegram_user_history', ['changed_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop index
    op.drop_index('ix_telegram_user_history_changed_at', table_name='telegram_user_history')

    # Drop table
    op.drop_table('telegram_user_history')
