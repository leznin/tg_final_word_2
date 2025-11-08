"""add_search_boost_tables

Revision ID: e24501900f6a
Revises: c551d800d073
Create Date: 2025-11-08 15:20:03.104174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e24501900f6a'
down_revision: Union[str, Sequence[str], None] = 'c551d800d073'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create search_boost_prices table
    op.create_table(
        'search_boost_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('boost_amount', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('price_stars', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='XTR'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_search_boost_prices_is_active', 'search_boost_prices', ['is_active'])
    
    # Create search_boost_purchases table
    op.create_table(
        'search_boost_purchases',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('telegram_user_id', sa.Integer(), nullable=False),
        sa.Column('boost_amount', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('price_stars', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), nullable=False, server_default='XTR'),
        sa.Column('telegram_payment_charge_id', sa.String(length=255), nullable=True),
        sa.Column('purchased_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('used_searches', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='true'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_search_boost_purchases_user_id', 'search_boost_purchases', ['user_id'])
    op.create_index('ix_search_boost_purchases_telegram_user_id', 'search_boost_purchases', ['telegram_user_id'])
    op.create_index('ix_search_boost_purchases_purchased_at', 'search_boost_purchases', ['purchased_at'])
    
    # Insert default price (can be changed in admin panel)
    op.execute(
        "INSERT INTO search_boost_prices (boost_amount, price_stars, currency, is_active) "
        "VALUES (10, 50, 'XTR', true)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('ix_search_boost_purchases_purchased_at', table_name='search_boost_purchases')
    op.drop_index('ix_search_boost_purchases_telegram_user_id', table_name='search_boost_purchases')
    op.drop_index('ix_search_boost_purchases_user_id', table_name='search_boost_purchases')
    op.drop_table('search_boost_purchases')
    
    op.drop_index('ix_search_boost_prices_is_active', table_name='search_boost_prices')
    op.drop_table('search_boost_prices')
