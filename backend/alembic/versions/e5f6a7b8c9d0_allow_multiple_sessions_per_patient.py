"""allow multiple sessions per patient

Revision ID: e5f6a7b8c9d0
Revises: d4e5f6a7b8c9
Create Date: 2026-04-01 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = "e5f6a7b8c9d0"
down_revision: Union[str, Sequence[str], None] = "d4e5f6a7b8c9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    unique_constraints = inspector.get_unique_constraints("sessions")

    for constraint in unique_constraints:
        columns = constraint.get("column_names") or []
        name = constraint.get("name")
        if columns == ["patient_id"] and name:
            op.drop_constraint(name, "sessions", type_="unique")
            break


def downgrade() -> None:
    op.create_unique_constraint(
        "uq_sessions_patient_id",
        "sessions",
        ["patient_id"],
    )
