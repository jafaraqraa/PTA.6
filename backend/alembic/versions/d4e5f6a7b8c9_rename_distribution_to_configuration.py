"""rename distribution to configuration

Revision ID: d4e5f6a7b8c9
Revises: c3d4e5f6a7b8
Create Date: 2026-03-31 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d4e5f6a7b8c9"
down_revision: Union[str, Sequence[str], None] = "c3d4e5f6a7b8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


HEARING_CONFIGURATION_ENUM = sa.Enum(
    "ALL_FREQUENCIES",
    "LOW_FREQUENCIES",
    "MID_FREQUENCIES",
    "HIGH_FREQUENCIES",
    "SINGLE_FREQUENCY",
    "NOTCH_PATTERN",
    "OTHER",
    "UNDETERMINED",
    name="hearingdistributionenum",
)


def upgrade() -> None:
    op.alter_column(
        "final_interpretations",
        "distribution",
        new_column_name="configuration",
        existing_type=HEARING_CONFIGURATION_ENUM,
        existing_nullable=True,
    )
    op.drop_column("final_interpretations", "air_bone_gap_present")
    op.drop_column("final_interpretations", "masking_was_needed")


def downgrade() -> None:
    op.add_column(
        "final_interpretations",
        sa.Column("masking_was_needed", sa.Boolean(), nullable=True),
    )
    op.add_column(
        "final_interpretations",
        sa.Column("air_bone_gap_present", sa.Boolean(), nullable=True),
    )
    op.alter_column(
        "final_interpretations",
        "configuration",
        new_column_name="distribution",
        existing_type=HEARING_CONFIGURATION_ENUM,
        existing_nullable=True,
    )
