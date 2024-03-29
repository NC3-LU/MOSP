"""added new collection table

Revision ID: 2c5b93302e8b
Revises: 88304952e3ff
Create Date: 2021-09-21 09:37:37.683935

"""
import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "2c5b93302e8b"
down_revision = "88304952e3ff"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "collection",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=500), nullable=True),
        sa.Column("date_created", sa.DateTime(), nullable=True),
        sa.Column("last_updated", sa.DateTime(), nullable=True),
        sa.Column("creator_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["creator_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
        sa.UniqueConstraint("uuid"),
    )
    op.create_table(
        "association_jsonobjects_collections",
        sa.Column("json_object_id", sa.Integer(), nullable=True),
        sa.Column("collection_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["collection_id"],
            ["collection.id"],
        ),
        sa.ForeignKeyConstraint(
            ["json_object_id"],
            ["json_object.id"],
        ),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("association_jsonobjects_collections")
    op.drop_table("collection")
    # ### end Alembic commands ###
