"""add_cv_column_to_users

Revision ID: 287e090bf5a2
Revises: 15aa1ce1cb50
Create Date: 2025-10-11 21:11:22.854269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '287e090bf5a2'
down_revision: Union[str, Sequence[str], None] = '15aa1ce1cb50'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add cv column to users table
    op.add_column('users', sa.Column('cv', sa.Text(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove cv column from users table
    op.drop_column('users', 'cv')
