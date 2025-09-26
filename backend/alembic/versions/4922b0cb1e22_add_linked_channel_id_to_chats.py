"""add_linked_channel_id_to_chats

Revision ID: 4922b0cb1e22
Revises: 
Create Date: 2025-09-25 21:08:12.936613

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4922b0cb1e22'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add linked_channel_id column to chats table
    op.add_column('chats', sa.Column('linked_channel_id', sa.Integer(), sa.ForeignKey('chats.id'), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove linked_channel_id column from chats table
    op.drop_column('chats', 'linked_channel_id')
