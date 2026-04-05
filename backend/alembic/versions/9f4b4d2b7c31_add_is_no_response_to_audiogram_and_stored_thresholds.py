"""add is_no_response to audiogram_points and stored_thresholds

Revision ID: 9f4b4d2b7c31
Revises: 2d2147f149f0
Create Date: 2026-03-24 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "9f4b4d2b7c31"
down_revision: Union[str, Sequence[str], None] = "2d2147f149f0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    with op.batch_alter_table('audiogram_points', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_no_response', sa.Boolean(), nullable=False, server_default=sa.false()))

    with op.batch_alter_table('stored_thresholds', schema=None) as batch_op:
        batch_op.add_column(sa.Column('is_no_response', sa.Boolean(), nullable=False, server_default=sa.false()))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("stored_thresholds", "is_no_response")
    op.drop_column("audiogram_points", "is_no_response")
