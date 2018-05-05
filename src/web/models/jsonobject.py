
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSON

from bootstrap import db

class JsonObject(db.Model):
    """Represent a JSON object.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    description = db.Column(db.String())
    is_public = db.Column(db.Boolean(), default=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())
    json_object = db.Column(JSON, default=None)

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                           default=None)
    schema_id = db.Column(db.Integer(), db.ForeignKey('schema.id'),
                           default=None)
