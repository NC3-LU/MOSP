from functools import wraps
from flask import abort
from flask_login import current_user
from mosp.models import JsonObject, Organization, Collection


def check_object_edit_permission(f):
    """Check if the user has permission to edit/delete the requested
    JsonObject."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)

        object_id = kwargs.get("object_id", None)
        if object_id is None:
            # user wants to create an object, not edit an existing:
            # no need to check the permissions
            return f(*args, **kwargs)

        # check if the authenticated user is part of the organization owning the object
        obj = JsonObject.query.filter(JsonObject.id == object_id).filter(
            JsonObject.organization.has(
                Organization.id.in_([org.id for org in current_user.organizations])
            )
        )
        if not obj.first():
            return abort(403)

        # check if the object is locked: only its creator can edit it
        if (
            obj.first()
            and obj.first().is_locked
            and obj.first().creator_id != current_user.id
        ):
            return abort(403)

        return f(*args, **kwargs)

    return decorated_function


def check_collection_edit_permission(f):
    """Check if the user has permission to edit/delete the requested
    collection.
    A collection can only be updated by its creator."""

    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated:
            return abort(403)

        collection_id = kwargs.get("collection_id", None)
        if collection_id is None:
            # user wants to create a collection, not edit an existing:
            # no need to check the permissions
            return f(*args, **kwargs)

        obj = Collection.query.filter(Collection.id == collection_id).first()
        if not obj:
            return abort(403)

        # check if the authenticated user is the owner of the collection
        if obj.creator_id != current_user.id:
            return abort(403)

        return f(*args, **kwargs)

    return decorated_function
