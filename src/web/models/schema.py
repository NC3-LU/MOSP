
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB

from bootstrap import db

class Schema(db.Model):
    """Represent a JSON schema.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(500))
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())
    json_schema = db.Column(JSONB, default={})

    # relationship
    objects = db.relationship('JsonObject', backref='schema', lazy='dynamic',
                               cascade='all,delete-orphan')

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                        default=None)
    creator_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                           default=None)
