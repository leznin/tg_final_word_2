"""add_subscription_prices_and_chat_subscriptions_tables

Revision ID: d4f8c9a1b2e3
Revises: b2f5bd880aa5
Create Date: 2025-09-30 12:30:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd4f8c9a1b2e3'
down_revision: Union[str, Sequence[str], None] = 'b2f5bd880aa5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create subscription_prices table
    op.create_table('subscription_prices',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('subscription_type', sa.String(length=20), nullable=False),
        sa.Column('price_stars', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='XTR', nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for subscription_prices
    op.create_index('ix_subscription_prices_subscription_type', 'subscription_prices', ['subscription_type'], unique=False)
    op.create_index('ix_subscription_prices_is_active', 'subscription_prices', ['is_active'], unique=False)

    # Create chat_subscriptions table
    op.create_table('chat_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('subscription_type', sa.String(length=20), nullable=False),
        sa.Column('price_stars', sa.Integer(), nullable=False),
        sa.Column('currency', sa.String(length=10), server_default='XTR', nullable=False),
        sa.Column('start_date', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('is_active', sa.Boolean(), server_default=sa.text('true'), nullable=False),
        sa.Column('telegram_payment_charge_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['chat_id'], ['chats.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    # Create indexes for chat_subscriptions
    op.create_index('ix_chat_subscriptions_chat_id', 'chat_subscriptions', ['chat_id'], unique=False)
    op.create_index('ix_chat_subscriptions_is_active', 'chat_subscriptions', ['is_active'], unique=False)
    op.create_index('ix_chat_subscriptions_end_date', 'chat_subscriptions', ['end_date'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes for chat_subscriptions
    op.drop_index('ix_chat_subscriptions_end_date', table_name='chat_subscriptions')
    op.drop_index('ix_chat_subscriptions_is_active', table_name='chat_subscriptions')
    op.drop_index('ix_chat_subscriptions_chat_id', table_name='chat_subscriptions')
    # Drop chat_subscriptions table
    op.drop_table('chat_subscriptions')

    # Drop indexes for subscription_prices
    op.drop_index('ix_subscription_prices_is_active', table_name='subscription_prices')
    op.drop_index('ix_subscription_prices_subscription_type', table_name='subscription_prices')
    # Drop subscription_prices table
    op.drop_table('subscription_prices')



