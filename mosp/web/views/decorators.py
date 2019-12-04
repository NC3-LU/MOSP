from sqlalchemy import or_
from functools import wraps
from flask import abort
from flask_login import current_user
from models import JsonObject, Organization


def check_object_edit_permission(f):
    """Check if the user has permission to edit/delete the requested
    JsonObject."""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)
        object_id = kwargs.get('object_id', None)
        if object_id is None:
            # user wants to create an object, not edit one:
            # no need to check the permissions
            return f(*args, **kwargs)
        if current_user.is_authenticated:
            obj = JsonObject.query. \
                filter(JsonObject.id==object_id). \
                filter(JsonObject.organization. \
                has(Organization.id.in_([org.id for org in current_user.organizations])))
        if not obj.first():
            return abort(403)
        return f(*args, **kwargs)
    return decorated_function
