"""add_admin_users_table

Revision ID: f1a2b3c4d5e6
Revises: e90a03196078
Create Date: 2024-11-04 14:00:00.000000

"""
from typing import Sequence, Union
from passlib.context import CryptContext
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'f1a2b3c4d5e6'
down_revision: Union[str, Sequence[str], None] = 'e90a03196078'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create admin_users table
    op.create_table('admin_users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_admin_users_id'), 'admin_users', ['id'], unique=False)
    op.create_index(op.f('ix_admin_users_email'), 'admin_users', ['email'], unique=True)
    op.create_index(op.f('ix_admin_users_username'), 'admin_users', ['username'], unique=True)

    # Insert default admin user
    # Hash the password: 696578As!@#$
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed_password = pwd_context.hash("696578As!@#$")
    
    # Insert the default admin user
    op.execute(
        text(
            "INSERT INTO admin_users (username, email, password_hash, is_active) "
            "VALUES (:username, :email, :password_hash, :is_active)"
        ).bindparam(
            username=None,
            email="Maksimleznin30@gmail.com",
            password_hash=hashed_password,
            is_active=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_admin_users_username'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_email'), table_name='admin_users')
    op.drop_index(op.f('ix_admin_users_id'), table_name='admin_users')
    op.drop_table('admin_users')