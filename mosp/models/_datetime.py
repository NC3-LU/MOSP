from datetime import datetime
from datetime import timezone


def utcnow_naive() -> datetime:
    """Current UTC time as a naive datetime.

    The DateTime columns in this project are declared without timezone=True,
    so tz-aware values would fail to insert. Strip tzinfo after computing in
    UTC; this is the non-deprecated replacement for datetime.utcnow().
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
