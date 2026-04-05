"""restore required attempt for stored threshold

Revision ID: g7b8c9d0e1f2
Revises: f6a7b8c9d0e1
Create Date: 2026-04-04 00:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "g7b8c9d0e1f2"
down_revision: Union[str, Sequence[str], None] = "f6a7b8c9d0e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rows without a source attempt violate the intended PTA workflow.
    op.execute("DELETE FROM stored_thresholds WHERE attempt_id IS NULL")
    with op.batch_alter_table('stored_thresholds', schema=None) as batch_op:
        batch_op.alter_column('attempt_id', existing_type=sa.Integer(), nullable=False)
        batch_op.drop_constraint('fk_stored_thresholds_attempt_id_attempts_v2', type_='foreignkey')
        batch_op.create_foreign_key('fk_stored_thresholds_attempt_id_attempts', 'attempts', ['attempt_id'], ['id'], ondelete='CASCADE')


def downgrade() -> None:
    with op.batch_alter_table('stored_thresholds', schema=None) as batch_op:
        batch_op.alter_column('attempt_id', existing_type=sa.Integer(), nullable=True)
        batch_op.drop_constraint('fk_stored_thresholds_attempt_id_attempts', type_='foreignkey')
        batch_op.create_foreign_key('fk_stored_thresholds_attempt_id_attempts_v2', 'attempts', ['attempt_id'], ['id'], ondelete='SET NULL')
