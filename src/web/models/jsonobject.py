
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from web.models import User

from bootstrap import db

association_table_license = db.Table('association_jsonobjects_licenses',
    db.metadata,
    db.Column('json_object_id', db.Integer, db.ForeignKey('json_object.id')),
    db.Column('license_id', db.Integer, db.ForeignKey('license.id'))
)

class JsonObject(db.Model):
    """Represent a JSON object.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    is_public = db.Column(db.Boolean(), default=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())
    json_object = db.Column(JSONB, default={})

    # relationship
    licenses = db.relationship("License",
                            secondary=lambda: association_table_license,
                            backref="objects")

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                        nullable=False)
    creator_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                            nullable=False)
    schema_id = db.Column(db.Integer(), db.ForeignKey('schema.id'),
                            nullable=False)
