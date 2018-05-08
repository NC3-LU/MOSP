from web.views.api import v1
from web.views import views, session_mgmt
from web.views.admin import admin_bp
from web.views.schema import schema_bp, schemas_bp
from web.views.object import object_bp, objects_bp
from web.views.user import user_bp
from web.views.organization import organization_bp, organizations_bp

__all__ = ['views', 'session_mgmt']
