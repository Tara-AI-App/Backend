"""add_status_column_to_users

Revision ID: 15aa1ce1cb50
Revises: bfb7e7d76b83
Create Date: 2025-10-11 21:01:07.198073

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15aa1ce1cb50'
down_revision: Union[str, Sequence[str], None] = 'bfb7e7d76b83'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add status column to users table with default value True
    op.add_column('users', sa.Column('status', sa.Boolean(), nullable=False, server_default='true'))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove status column from users table
    op.drop_column('users', 'status')
