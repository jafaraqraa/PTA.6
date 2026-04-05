"""add final interpretations

Revision ID: c3d4e5f6a7b8
Revises: b2c3d4e5f6a7
Create Date: 2026-03-29 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c3d4e5f6a7b8"
down_revision: Union[str, Sequence[str], None] = "b2c3d4e5f6a7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    existing_ear_side_enum = postgresql.ENUM(
        "LEFT",
        "RIGHT",
        name="earsideenum",
        create_type=False,
    )
    existing_hearing_type_enum = postgresql.ENUM(
        "NORMAL",
        "CONDUCTIVE",
        "SENSORINEURAL",
        "MIXED",
        name="hearingtypeenum",
        create_type=False,
    )
    hearing_severity_enum = postgresql.ENUM(
        "NORMAL",
        "MILD",
        "MODERATE",
        "MODERATELY_SEVERE",
        "SEVERE",
        "PROFOUND",
        "UNDETERMINED",
        name="hearingseverityenum",
        create_type=False,
    )
    hearing_severity_enum.create(op.get_bind(), checkfirst=True)
    hearing_distribution_enum = postgresql.ENUM(
        "ALL_FREQUENCIES",
        "LOW_FREQUENCIES",
        "MID_FREQUENCIES",
        "HIGH_FREQUENCIES",
        "SINGLE_FREQUENCY",
        "NOTCH_PATTERN",
        "OTHER",
        "UNDETERMINED",
        name="hearingdistributionenum",
        create_type=False,
    )
    hearing_distribution_enum.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "final_interpretations",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("ear_side", existing_ear_side_enum, nullable=False),
        sa.Column(
            "overall_type",
            existing_hearing_type_enum,
            nullable=True,
        ),
        sa.Column(
            "severity",
            hearing_severity_enum,
            nullable=True,
        ),
        sa.Column(
            "distribution",
            hearing_distribution_enum,
            nullable=True,
        ),
        sa.Column("affected_frequencies_hz", sa.JSON(), nullable=False),
        sa.Column("air_bone_gap_present", sa.Boolean(), nullable=True),
        sa.Column("masking_was_needed", sa.Boolean(), nullable=True),
        sa.Column("clinical_comment", sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("session_id", "ear_side", name="uq_final_interpretation_session_ear"),
    )
    op.create_index(op.f("ix_final_interpretations_id"), "final_interpretations", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_final_interpretations_id"), table_name="final_interpretations")
    op.drop_table("final_interpretations")
