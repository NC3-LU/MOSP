from mosp.views import session_mgmt
from mosp.views import views
from mosp.views.admin import admin_bp
from mosp.views.collection import collection_bp
from mosp.views.collection import collections_bp
from mosp.views.object import object_bp
from mosp.views.object import objects_bp
from mosp.views.organization import organization_bp
from mosp.views.organization import organizations_bp
from mosp.views.schema import schema_bp
from mosp.views.schema import schemas_bp
from mosp.views.stats import stats_bp
from mosp.views.user import user_bp

__all__ = [
    "views",
    "session_mgmt",
    "admin_bp",
    "schema_bp",
    "schemas_bp",
    "object_bp",
    "objects_bp",
    "user_bp",
    "organization_bp",
    "organizations_bp",
    "stats_bp",
    "collection_bp",
    "collections_bp",
]
