"""create_manager_chat_access_table

Revision ID: a35560e6926e
Revises: e388c16c0e48
Create Date: 2025-11-05 18:21:53.727563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a35560e6926e'
down_revision: Union[str, Sequence[str], None] = 'e388c16c0e48'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create manager_chat_access table
    op.create_table(
        'manager_chat_access',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('admin_user_id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['admin_user_id'], ['admin_users.id'], ),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('admin_user_id', 'chat_id', name='uix_manager_chat')
    )
    op.create_index(op.f('ix_manager_chat_access_id'), 'manager_chat_access', ['id'], unique=False)
    op.create_index(op.f('ix_manager_chat_access_admin_user_id'), 'manager_chat_access', ['admin_user_id'], unique=False)
    op.create_index(op.f('ix_manager_chat_access_chat_id'), 'manager_chat_access', ['chat_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('ix_manager_chat_access_chat_id'), table_name='manager_chat_access')
    op.drop_index(op.f('ix_manager_chat_access_admin_user_id'), table_name='manager_chat_access')
    op.drop_index(op.f('ix_manager_chat_access_id'), table_name='manager_chat_access')
    # Drop table
    op.drop_table('manager_chat_access')
