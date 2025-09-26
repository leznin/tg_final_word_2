"""add_auth_attempts_table

Revision ID: add_auth_attempts_001
Revises: 2ac7bbd13a29
Create Date: 2025-09-26 18:15:15.420364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'add_auth_attempts_001'
down_revision: Union[str, Sequence[str], None] = '2ac7bbd13a29'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('auth_attempts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fingerprint', sa.String(length=255), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('success', sa.Boolean(), nullable=True),
        sa.Column('blocked', sa.Boolean(), nullable=True),
        sa.Column('block_reason', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_auth_attempts_fingerprint', 'fingerprint')
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table('auth_attempts')
