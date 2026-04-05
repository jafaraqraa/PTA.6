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


def _drop_attempt_fk_if_exists() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    foreign_keys = inspector.get_foreign_keys("stored_thresholds")
    for fk in foreign_keys:
        constrained = fk.get("constrained_columns") or []
        name = fk.get("name")
        referred_table = fk.get("referred_table")
        if constrained == ["attempt_id"] and referred_table == "attempts" and name:
            op.drop_constraint(name, "stored_thresholds", type_="foreignkey")
            break


def upgrade() -> None:
    # Rows without a source attempt violate the intended PTA workflow.
    op.execute("DELETE FROM stored_thresholds WHERE attempt_id IS NULL")
    _drop_attempt_fk_if_exists()
    op.alter_column(
        "stored_thresholds",
        "attempt_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_stored_thresholds_attempt_id_attempts",
        "stored_thresholds",
        "attempts",
        ["attempt_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    _drop_attempt_fk_if_exists()
    op.alter_column(
        "stored_thresholds",
        "attempt_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.create_foreign_key(
        "fk_stored_thresholds_attempt_id_attempts",
        "stored_thresholds",
        "attempts",
        ["attempt_id"],
        ["id"],
        ondelete="SET NULL",
    )
