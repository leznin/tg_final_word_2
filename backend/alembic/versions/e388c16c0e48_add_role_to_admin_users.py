"""add_role_to_admin_users

Revision ID: e388c16c0e48
Revises: 9952f62943fb
Create Date: 2025-11-05 18:21:20.919208

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e388c16c0e48'
down_revision: Union[str, Sequence[str], None] = '9952f62943fb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add role column to admin_users table
    op.add_column('admin_users', sa.Column('role', sa.String(length=20), nullable=False, server_default='admin'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove role column from admin_users table
    op.drop_column('admin_users', 'role')
