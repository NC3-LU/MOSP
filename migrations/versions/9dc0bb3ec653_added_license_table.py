"""Added license table.

Revision ID: 9dc0bb3ec653
Revises:
Create Date: 2018-10-04 09:44:55.857714

"""
from datetime import datetime

import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "9dc0bb3ec653"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "license",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), default=""),
        sa.Column("license_id", sa.String(), default=""),
        sa.Column("created_at", sa.DateTime(), default=datetime.utcnow),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "association_schemas_licenses",
        sa.Column("schema_id", sa.Integer(), sa.ForeignKey("schema.id")),
        sa.Column("license_id", sa.Integer(), sa.ForeignKey("license.id")),
    )
    op.create_table(
        "association_jsonobjects_licenses",
        sa.Column("json_object_id", sa.Integer(), sa.ForeignKey("json_object.id")),
        sa.Column("license_id", sa.Integer(), sa.ForeignKey("license.id")),
    )


def downgrade():
    op.drop_table("license")
    op.drop_table("association_schemas_licenses")
    op.drop_table("association_jsonobjects_licenses")
