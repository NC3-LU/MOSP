from datetime import datetime
from datetime import timezone

from mosp.bootstrap import db


class License(db.Model):
    """Represent a license.
    https://opensource.org/licenses/alphabetical
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), default="", nullable=False, unique=True)
    license_id = db.Column(db.String(), default="", nullable=False, unique=True)
    created_at = db.Column(
        db.DateTime(), default=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def __str__(self):
        return self.name
