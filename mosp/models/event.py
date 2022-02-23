from datetime import datetime

from mosp.bootstrap import db


class Event(db.Model):
    """Represent an event."""

    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(), nullable=False)
    action = db.Column(db.String(), nullable=False)
    subject = db.Column(db.String(), nullable=False)
    initiator = db.Column(db.String())
    date = db.Column(db.DateTime(), default=datetime.utcnow)
