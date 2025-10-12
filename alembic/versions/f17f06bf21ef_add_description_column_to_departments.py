"""add_description_column_to_departments

Revision ID: f17f06bf21ef
Revises: 287e090bf5a2
Create Date: 2025-10-12 03:54:35.427916

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f17f06bf21ef'
down_revision: Union[str, Sequence[str], None] = '287e090bf5a2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add description column to departments table
    op.add_column('departments', sa.Column('description', sa.String(500), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove description column from departments table
    op.drop_column('departments', 'description')
