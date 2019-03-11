"""Add a new association table to link objects.

Revision ID: fb48dfd74687
Revises: 9dc0bb3ec653
Create Date: 2019-03-11 14:15:01.569402

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fb48dfd74687'
down_revision = '9dc0bb3ec653'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('association_jsonobject_jsonobject',
            sa.Column('jsonobject_refers_to_id', sa.Integer(),
                        sa.ForeignKey('json_object.id')),
            sa.Column('jsonobject_referred_to_by_id', sa.Integer(),
                        sa.ForeignKey('json_object.id'))
    )


def downgrade():
    op.drop_table('association_projects_projects')
