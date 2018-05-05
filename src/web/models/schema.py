
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

from bootstrap import db
from web.models import JsonObject

class Schema(db.Model):
    """Represent a JSON schema.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    is_public = db.Column(db.Boolean(), default=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())
    json_schema = db.Column(JSON, default=None)

    # relationship
    objects = db.relationship(JsonObject, backref='schema', lazy='dynamic',
                               cascade='all,delete-orphan')

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                           default=None)
