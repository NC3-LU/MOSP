"""Remove_is_public_attribute_from_json_object

Revision ID: 7a6232889a35
Revises: 2af9469ca54d
Create Date: 2019-05-21 15:03:07.409574

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '7a6232889a35'
down_revision = '2af9469ca54d'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_column('json_object', 'is_public')


def downgrade():
    op.add_column('json_object', sa.Column('is_public', sa.Boolean(),
                  default=True))
