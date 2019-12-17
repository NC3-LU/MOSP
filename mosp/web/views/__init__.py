from mosp.web.views.api import v1
from mosp.web.views import views, session_mgmt
from mosp.web.views.admin import admin_bp
from mosp.web.views.schema import schema_bp, schemas_bp
from mosp.web.views.object import object_bp, objects_bp
from mosp.web.views.user import user_bp
from mosp.web.views.organization import organization_bp, organizations_bp

__all__ = ["views", "session_mgmt"]
