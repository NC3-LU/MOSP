#! /usr/bin/env python
# -*- coding: utf-8 -*-

import uuid
from flask import request
from flask_login import current_user
from flask_restx import abort, fields

from mosp.models import User
from mosp.views.common import login_user_bundle


def auth_func(func):
    """Authentication decorator."""

    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            if "X-API-KEY" in request.headers:
                token = request.headers.get("X-API-KEY", False)
                if token:
                    user = User.query.filter(User.apikey == token).first()
                    if not user:
                        abort(401, Error="Unauthorized.")
                    if not user.is_active:
                        abort(403, Error="Account is not active.")
                    login_user_bundle(user)
            else:
                abort(401, Error="Authentication required.")
        return func(*args, **kwargs)

    wrapper.__doc__ = func.__doc__
    wrapper.__name__ = func.__name__
    return wrapper


def uuid_type(value):
    """Parse UUID"""
    try:
        val = uuid.UUID(value)
    except ValueError:
        raise ValueError("This is not a valid UUID.")
    return val


# Params for models marshalling

metada_params_model = {
    "count": fields.String(
        readonly=True, description="Total number of the items of the data."
    ),
    "offset": fields.String(
        readonly=True,
        description="Position of the first element of the data from the total data amount.",
    ),
    "limit": fields.String(readonly=True, description="Requested limit data."),
}

organization_params_model = {
    "id": fields.Integer(description="Organization id.", readonly=True),
    "name": fields.String(description="The organization name."),
    "description": fields.String(description="The organization description."),
    "organization_type": fields.String(description="The type of the organization."),
    "is_membership_restricted": fields.Boolean(
        description="The membership model of the organization (restricted or not restricted)."
    ),
    "last_updated": fields.DateTime(description="Updated time of the schema."),
}

object_params_model = {
    "id": fields.Integer(description="Object id.", readonly=True),
    "name": fields.String(description="Object name."),
    "description": fields.String(description="Object description."),
    # "organization": fields.Nested(organization_params_model),
    "schema_id": fields.Integer(description="Id of the schema validating the object."),
    "org_id": fields.Integer(description="Id of the organization owning the object."),
    "last_updated": fields.DateTime(
        description="Updated time of the object.", readonly=True
    ),
    "json_object": fields.Raw(description="The JSON object."),
}

schema_params_model = {
    "id": fields.Integer(description="Schema id.", readonly=True),
    "name": fields.String(description="The schema name."),
    "description": fields.String(description="The schema description."),
    # "organization": fields.Nested(organization_params_model),
    "last_updated": fields.DateTime(description="Updated time of the schema."),
    "json_schema": fields.Raw(description="The schena."),
}

user_params_model = {
    "id": fields.Integer(description="User id.", readonly=True),
    "login": fields.String(description="The user login."),
    "created_at": fields.DateTime(description="The date of creation of the user."),
    "last_seen": fields.DateTime(
        description="The date of last connection of the user."
    ),
    # "organizations": fields.List(
    #     fields.Nested(organization_params_model), description="List of organizations."
    # ),
}

license_params_model = {
    # "id": fields.Integer(description="License id."),
    # "name": fields.String(description="The license name."),
    "license_id": fields.String(description="The SPDX license id."),
}

version_params_model = {
    "id": fields.Integer(description="Version id.", readonly=True),
    "name": fields.String(description="The object name."),
    "last_updated": fields.DateTime(description="Updated time of the schema."),
}

collection_params_model = {
    "id": fields.Integer(description="Collection id.", readonly=True),
    "uuid": fields.String(description="Collection UUID.", readonly=True),
    "name": fields.String(description="The object name."),
    "last_updated": fields.DateTime(description="Updated time of the collection."),
}
