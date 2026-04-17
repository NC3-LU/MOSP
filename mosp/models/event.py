from sqlalchemy.orm import validates

from mosp.bootstrap import db
from mosp.models._datetime import utcnow_naive


class Event(db.Model):
    """Represent an event."""

    id = db.Column(db.Integer, primary_key=True)
    scope = db.Column(db.String(), nullable=False)
    action = db.Column(db.String(), nullable=False)
    subject = db.Column(db.String(), nullable=False)
    initiator = db.Column(db.String())
    date = db.Column(db.DateTime(), default=utcnow_naive)

    @validates("initiator")
    def validates_initiator(self, key: str, value: str):
        if any(
            bot in value
            for bot in [
                "robot",
                "SemrushBot",
                "AhrefsBot",
                "Googlebot",
                "bingbot",
                "DotBot",
                "Twitterbot",
                "YandexBot",
                "Applebot",
            ]
        ):
            raise AssertionError("do not log event initiated by bots")
        return value
