"""add_user_search_logs_table

Revision ID: c551d800d073
Revises: cb6178072e4b
Create Date: 2025-11-08 15:05:32.975075

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c551d800d073'
down_revision: Union[str, Sequence[str], None] = 'cb6178072e4b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'user_search_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.Integer(), nullable=False),
        sa.Column('search_query', sa.String(length=255), nullable=False),
        sa.Column('results_count', sa.Integer(), server_default='0', nullable=True),
        sa.Column('searched_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_search_logs_id'), 'user_search_logs', ['id'], unique=False)
    op.create_index(op.f('ix_user_search_logs_searched_at'), 'user_search_logs', ['searched_at'], unique=False)
    op.create_index(op.f('ix_user_search_logs_telegram_user_id'), 'user_search_logs', ['telegram_user_id'], unique=False)
    op.create_index(op.f('ix_user_search_logs_user_id'), 'user_search_logs', ['user_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_user_search_logs_user_id'), table_name='user_search_logs')
    op.drop_index(op.f('ix_user_search_logs_telegram_user_id'), table_name='user_search_logs')
    op.drop_index(op.f('ix_user_search_logs_searched_at'), table_name='user_search_logs')
    op.drop_index(op.f('ix_user_search_logs_id'), table_name='user_search_logs')
    op.drop_table('user_search_logs')
