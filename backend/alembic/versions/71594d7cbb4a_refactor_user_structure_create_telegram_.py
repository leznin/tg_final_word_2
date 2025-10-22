"""refactor_user_structure_create_telegram_users_and_changes_tables

Revision ID: 71594d7cbb4a
Revises: b0f163137fda
Create Date: 2025-10-21 17:13:38.265563

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '71594d7cbb4a'
down_revision: Union[str, Sequence[str], None] = 'b0f163137fda'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create telegram_users table
    op.create_table('telegram_users',
        sa.Column('telegram_user_id', sa.BigInteger(), nullable=False),
        sa.Column('is_bot', sa.Boolean(), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.Column('username', sa.String(length=255), nullable=True),
        sa.Column('language_code', sa.String(length=10), nullable=True),
        sa.Column('is_premium', sa.Boolean(), nullable=True),
        sa.Column('added_to_attachment_menu', sa.Boolean(), nullable=True),
        sa.Column('can_join_groups', sa.Boolean(), nullable=True),
        sa.Column('can_read_all_group_messages', sa.Boolean(), nullable=True),
        sa.Column('supports_inline_queries', sa.Boolean(), nullable=True),
        sa.Column('can_connect_to_business', sa.Boolean(), nullable=True),
        sa.Column('has_main_web_app', sa.Boolean(), nullable=True),
        sa.Column('account_creation_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('telegram_user_id')
    )

    # Create indexes for telegram_users
    op.create_index('ix_telegram_users_telegram_user_id', 'telegram_users', ['telegram_user_id'], unique=True)
    op.create_index('ix_telegram_users_username', 'telegram_users', ['username'], unique=False)

    # Add foreign key to chat_members
    op.add_column('chat_members', sa.Column('telegram_user_id_fk', sa.BigInteger(), nullable=True))
    op.create_foreign_key('fk_chat_members_telegram_user_id', 'chat_members', 'telegram_users', ['telegram_user_id_fk'], ['telegram_user_id'])

    # Migrate data from chat_members to telegram_users
    # First, insert unique users from chat_members
    op.execute("""
        INSERT INTO telegram_users (
            telegram_user_id, is_bot, first_name, last_name, username,
            language_code, is_premium, added_to_attachment_menu,
            can_join_groups, can_read_all_group_messages,
            supports_inline_queries, can_connect_to_business,
            has_main_web_app, account_creation_date, created_at, updated_at
        )
        SELECT DISTINCT
            cm.telegram_user_id, cm.is_bot, cm.first_name, cm.last_name, cm.username,
            cm.language_code, cm.is_premium, cm.added_to_attachment_menu,
            cm.can_join_groups, cm.can_read_all_group_messages,
            cm.supports_inline_queries, cm.can_connect_to_business,
            cm.has_main_web_app, cm.account_creation_date, cm.created_at, cm.updated_at
        FROM chat_members cm
        WHERE cm.telegram_user_id NOT IN (SELECT telegram_user_id FROM telegram_users)
    """)

    # Update chat_members to reference telegram_users
    # Since we just inserted data into telegram_users with the same telegram_user_id values
    # from chat_members, we can simply set telegram_user_id_fk = telegram_user_id
    op.execute("""
        UPDATE chat_members
        SET telegram_user_id_fk = telegram_user_id
    """)

    # Drop duplicate columns from chat_members (they are now in telegram_users)
    op.drop_column('chat_members', 'is_bot')
    op.drop_column('chat_members', 'first_name')
    op.drop_column('chat_members', 'last_name')
    op.drop_column('chat_members', 'username')
    op.drop_column('chat_members', 'language_code')
    op.drop_column('chat_members', 'is_premium')
    op.drop_column('chat_members', 'added_to_attachment_menu')
    op.drop_column('chat_members', 'can_join_groups')
    op.drop_column('chat_members', 'can_read_all_group_messages')
    op.drop_column('chat_members', 'supports_inline_queries')
    op.drop_column('chat_members', 'can_connect_to_business')
    op.drop_column('chat_members', 'has_main_web_app')
    op.drop_column('chat_members', 'account_creation_date')

    # Drop old telegram_user_id column and rename telegram_user_id_fk to telegram_user_id
    op.drop_column('chat_members', 'telegram_user_id')
    op.alter_column('chat_members', 'telegram_user_id_fk', new_column_name='telegram_user_id', existing_type=sa.BigInteger())

    # Make telegram_user_id NOT NULL
    op.alter_column('chat_members', 'telegram_user_id', nullable=False)

    # Recreate unique constraint for chat_members
    op.drop_constraint('unique_chat_member', 'chat_members', type_='unique')
    op.create_unique_constraint('unique_chat_member', 'chat_members', ['chat_id', 'telegram_user_id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop unique constraint
    op.drop_constraint('unique_chat_member', 'chat_members', type_='unique')

    # Add back the old telegram_user_id column (temporary)
    op.add_column('chat_members', sa.Column('old_telegram_user_id', sa.BigInteger(), nullable=True))

    # Copy current telegram_user_id values to old_telegram_user_id
    op.execute("""
        UPDATE chat_members
        SET old_telegram_user_id = telegram_user_id
    """)

    # Add back all the duplicate columns to chat_members
    op.add_column('chat_members', sa.Column('is_bot', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('first_name', sa.String(length=255), nullable=True))
    op.add_column('chat_members', sa.Column('last_name', sa.String(length=255), nullable=True))
    op.add_column('chat_members', sa.Column('username', sa.String(length=255), nullable=True))
    op.add_column('chat_members', sa.Column('language_code', sa.String(length=10), nullable=True))
    op.add_column('chat_members', sa.Column('is_premium', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('added_to_attachment_menu', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('can_join_groups', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('can_read_all_group_messages', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('supports_inline_queries', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('can_connect_to_business', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('has_main_web_app', sa.Boolean(), nullable=True))
    op.add_column('chat_members', sa.Column('account_creation_date', sa.DateTime(timezone=True), nullable=True))

    # Migrate data back from telegram_users to chat_members
    op.execute("""
        UPDATE chat_members cm
        SET
            is_bot = tu.is_bot,
            first_name = tu.first_name,
            last_name = tu.last_name,
            username = tu.username,
            language_code = tu.language_code,
            is_premium = tu.is_premium,
            added_to_attachment_menu = tu.added_to_attachment_menu,
            can_join_groups = tu.can_join_groups,
            can_read_all_group_messages = tu.can_read_all_group_messages,
            supports_inline_queries = tu.supports_inline_queries,
            can_connect_to_business = tu.can_connect_to_business,
            has_main_web_app = tu.has_main_web_app,
            account_creation_date = tu.account_creation_date
        FROM telegram_users tu
        WHERE cm.telegram_user_id = tu.telegram_user_id
    """)

    # Drop foreign key constraint
    op.drop_constraint('fk_chat_members_telegram_user_id', 'chat_members', type_='foreignkey')

    # Drop current telegram_user_id column and rename old_telegram_user_id back
    op.drop_column('chat_members', 'telegram_user_id')
    op.alter_column('chat_members', 'old_telegram_user_id', new_column_name='telegram_user_id', existing_type=sa.BigInteger())

    # Make telegram_user_id NOT NULL
    op.alter_column('chat_members', 'telegram_user_id', nullable=False)

    # Recreate unique constraint
    op.create_unique_constraint('unique_chat_member', 'chat_members', ['chat_id', 'telegram_user_id'])

    # Drop telegram_users table and its indexes
    op.drop_index('ix_telegram_users_username', table_name='telegram_users')
    op.drop_index('ix_telegram_users_telegram_user_id', table_name='telegram_users')
    op.drop_table('telegram_users')
