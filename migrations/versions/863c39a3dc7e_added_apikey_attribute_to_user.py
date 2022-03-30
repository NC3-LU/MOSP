"""Added apikey attribute to User.

Revision ID: 863c39a3dc7e
Revises: 7a6232889a35
Create Date: 2019-12-18 11:47:00.949616

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "863c39a3dc7e"
down_revision = "7a6232889a35"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("user", sa.Column("apikey", sa.String(), default=""))


def downgrade():
    op.drop_column("user", "apikey")
