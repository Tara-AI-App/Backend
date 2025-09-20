"""add_oauth_tokens_table

Revision ID: 4b5c6d7e8f90
Revises: 3a475843ad39
Create Date: 2025-01-27 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4b5c6d7e8f90'
down_revision: Union[str, Sequence[str], None] = '3a475843ad39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create user_oauth_tokens table
    op.create_table('user_oauth_tokens',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('uuid_generate_v4()')),
    sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('provider', sa.String(length=50), nullable=False),
    sa.Column('access_token', sa.Text(), nullable=False),
    sa.Column('refresh_token', sa.Text(), nullable=True),
    sa.Column('token_type', sa.String(length=50), nullable=True),
    sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_oauth_tokens_id'), 'user_oauth_tokens', ['id'], unique=False)
    op.create_index(op.f('ix_user_oauth_tokens_user_id'), 'user_oauth_tokens', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_oauth_tokens_provider'), 'user_oauth_tokens', ['provider'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop user_oauth_tokens table
    op.drop_index(op.f('ix_user_oauth_tokens_provider'), table_name='user_oauth_tokens')
    op.drop_index(op.f('ix_user_oauth_tokens_user_id'), table_name='user_oauth_tokens')
    op.drop_index(op.f('ix_user_oauth_tokens_id'), table_name='user_oauth_tokens')
    op.drop_table('user_oauth_tokens')
