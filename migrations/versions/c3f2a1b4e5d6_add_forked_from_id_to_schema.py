"""add forked_from_id to schema

Revision ID: c3f2a1b4e5d6
Revises: 44015f761a68
Create Date: 2026-04-15 15:30:00.000000

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "c3f2a1b4e5d6"
down_revision = "44015f761a68"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "schema",
        sa.Column("forked_from_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_schema_forked_from_id",
        "schema",
        "schema",
        ["forked_from_id"],
        ["id"],
    )


def downgrade():
    op.drop_constraint("fk_schema_forked_from_id", "schema", type_="foreignkey")
    op.drop_column("schema", "forked_from_id")
