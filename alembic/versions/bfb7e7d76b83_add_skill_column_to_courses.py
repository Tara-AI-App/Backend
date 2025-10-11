"""add_skill_column_to_courses

Revision ID: bfb7e7d76b83
Revises: 74cfcb753fab
Create Date: 2025-10-11 15:51:51.584930

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bfb7e7d76b83'
down_revision: Union[str, Sequence[str], None] = '74cfcb753fab'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Add skill column to courses table as array of strings
    op.add_column('courses', sa.Column('skill', sa.ARRAY(sa.String), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    # Remove skill column from courses table
    op.drop_column('courses', 'skill')
