"""add_openrouter_settings_table

Revision ID: 8fcb0d9d50db
Revises: 0da5c1835864
Create Date: 2025-09-28 16:54:05.767201

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8fcb0d9d50db'
down_revision: Union[str, Sequence[str], None] = '0da5c1835864'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table('openrouter_settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('api_key', sa.String(length=255), nullable=False),
        sa.Column('selected_model', sa.String(length=100), nullable=True),
        sa.Column('balance', sa.Float(), nullable=True),
        sa.Column('prompt', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes
    op.create_index('ix_openrouter_settings_api_key', 'openrouter_settings', ['api_key'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index('ix_openrouter_settings_api_key', table_name='openrouter_settings')
    # Drop table
    op.drop_table('openrouter_settings')
