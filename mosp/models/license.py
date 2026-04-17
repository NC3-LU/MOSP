from mosp.bootstrap import db
from mosp.models._datetime import utcnow_naive


class License(db.Model):
    """Represent a license.
    https://opensource.org/licenses/alphabetical
    """

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), default="", nullable=False, unique=True)
    license_id = db.Column(db.String(), default="", nullable=False, unique=True)
    created_at = db.Column(db.DateTime(), default=utcnow_naive)

    def __str__(self):
        return self.name
