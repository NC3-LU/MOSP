"""Update type of some String column to Text

Revision ID: 2af9469ca54d
Revises: fb48dfd74687
Create Date: 2019-04-12 15:43:42.917501

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "2af9469ca54d"
down_revision = "fb48dfd74687"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "json_object",
        "name",
        existing_type=sa.String(length=100),
        type_=sa.Text(),
        existing_nullable=False,
    )
    op.alter_column(
        "json_object",
        "description",
        existing_type=sa.String(length=500),
        type_=sa.Text(),
        existing_nullable=False,
    )


def downgrade():
    op.alter_column(
        "json_object",
        "name",
        existing_type=sa.Text(),
        type_=sa.String(length=100),
        existing_nullable=False,
    )
    op.alter_column(
        "json_object",
        "description",
        existing_type=sa.Text(),
        type_=sa.String(length=500),
        existing_nullable=False,
    )
