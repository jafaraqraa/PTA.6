"""add hearing_profile and hearing_tags to ears

Revision ID: a1b2c3d4e5f6
Revises: 9f4b4d2b7c31
Create Date: 2026-03-25 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "9f4b4d2b7c31"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("ears", sa.Column("hearing_profile", sa.JSON(), nullable=True))
    op.add_column("ears", sa.Column("hearing_tags", sa.JSON(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("ears", "hearing_tags")
    op.drop_column("ears", "hearing_profile")

