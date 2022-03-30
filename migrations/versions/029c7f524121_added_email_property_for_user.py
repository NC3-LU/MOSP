"""added email property for user

Revision ID: 029c7f524121
Revises: 863c39a3dc7e
Create Date: 2020-04-07 10:33:31.459049

"""
import sqlalchemy as sa
from alembic import op


# revision identifiers, used by Alembic.
revision = "029c7f524121"
down_revision = "863c39a3dc7e"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("user", sa.Column("email", sa.String(length=256), nullable=True))
    op.get_bind().execute(
        'UPDATE "user" SET email=%s WHERE email IS NULL;', ("user@mosp.localhost")
    )
    op.alter_column("user", "email", nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("user", "email")
    # ### end Alembic commands ###
