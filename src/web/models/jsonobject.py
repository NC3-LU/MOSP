
from datetime import datetime
from sqlalchemy.dialects.postgresql import JSONB
from web.models import User

from bootstrap import db

class JsonObject(db.Model):
    """Represent a JSON object.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    is_public = db.Column(db.Boolean(), default=True)
    last_updated = db.Column(db.DateTime(), default=datetime.utcnow())
    json_object = db.Column(JSONB, default={})

    # foreign keys
    org_id = db.Column(db.Integer(), db.ForeignKey('organization.id'),
                        nullable=False)
    creator_id = db.Column(db.Integer(), db.ForeignKey('user.id'),
                            nullable=False)
    schema_id = db.Column(db.Integer(), db.ForeignKey('schema.id'),
                            nullable=False)
