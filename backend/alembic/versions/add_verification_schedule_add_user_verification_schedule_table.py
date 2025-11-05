"""add user verification schedule table

Revision ID: add_verification_schedule
Revises: 
Create Date: 2024-11-05 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'add_verification_schedule'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create user_verification_schedule table"""
    op.create_table(
        'user_verification_schedule',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('enabled', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('schedule_time', sa.Time(), nullable=False),
        sa.Column('interval_hours', sa.Integer(), nullable=False, server_default='24'),
        sa.Column('auto_update', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('chat_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('next_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_verification_schedule_id'), 'user_verification_schedule', ['id'], unique=False)


def downgrade() -> None:
    """Drop user_verification_schedule table"""
    op.drop_index(op.f('ix_user_verification_schedule_id'), table_name='user_verification_schedule')
    op.drop_table('user_verification_schedule')
