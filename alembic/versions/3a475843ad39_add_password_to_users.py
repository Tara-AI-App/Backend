"""add_password_to_users

Revision ID: 3a475843ad39
Revises: 1a9f4930e1d4
Create Date: 2025-09-13 16:09:20.383969

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3a475843ad39'
down_revision: Union[str, Sequence[str], None] = '1a9f4930e1d4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add password column to users table
    op.add_column('users', sa.Column('password', sa.String(length=255), nullable=False, server_default=''))
    
    # Remove the default value after adding the column
    op.alter_column('users', 'password', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove password column from users table
    op.drop_column('users', 'password')
