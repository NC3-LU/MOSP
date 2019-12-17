#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import jsonschema
from flask import request
from flask_login import current_user
from flask_restless import ProcessingException

from mosp.web.views.common import login_user_bundle
from mosp.models import User, Schema, JsonObject

logger = logging.getLogger(__name__)


def auth_func(*args, **kw):
    """
    Pre-processor used to check if a user is authenticated.
    """
    if request.authorization:
        user = User.query.filter(User.login == request.authorization.username).first()
        if not user:
            raise ProcessingException("Couldn't authenticate your user", code=401)
        if not user.check_password(request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user", code=401)
        if not user.is_active:
            raise ProcessingException("Couldn't authenticate your user", code=401)
        login_user_bundle(user)
    if not current_user.is_authenticated:
        raise ProcessingException(description="Not authenticated!", code=401)


def check_single_object_edit_permission(instance_id, data):
    """Pre-processor to edit a single object.
    """
    if not current_user.is_authenticated:
        raise ProcessingException(description="Not authenticated!", code=401)

    json_object = JsonObject.query.filter(JsonObject.id == instance_id).first()
    if json_object:
        # set the values requires by check_information()
        data["schema_id"] = json_object.schema.id
        data["org_id"] = json_object.organization.id
        data["creator_id"] = (
            json_object.creator.id if json_object.creator.id else current_user.id
        )
    else:
        raise ProcessingException(description="Unknown object", code=401)
    try:
        check_information(data)
    except Exception as e:
        raise (e)


def check_object_creation_permission(data):
    """Check if the user is authenticated and set the creator_id.
    """
    if not current_user.is_authenticated:
        raise ProcessingException(description="Not authenticated!", code=401)

    data["creator_id"] = current_user.id
    check_information(data)


def check_information(data):
    """Ensures. a user has the rights to create/edit an abject
    in a specific organization.
    Checks also the validity of the submitted JSON object against the specified
    the JSON schema.
    """
    schema_id = data.get("schema_id", None)
    org_id = data.get("org_id", None)

    if org_id is None:
        raise ProcessingException(
            description="You must provide the id of an organization.", code=400
        )
    if org_id not in [org.id for org in current_user.organizations]:
        raise ProcessingException(
            description="You are not allowed to create/edit object from this organization.",
            code=400,
        )

    if schema_id is None:
        raise ProcessingException(
            description="You must provide the id of a schema.", code=400
        )
    schema = Schema.query.filter(Schema.id == schema_id)
    if not schema.count():
        raise ProcessingException(description="Bad schema id", code=400)
    try:
        # check the validity of the submitted object
        # (note: an empty JSON object is validated by any schema)
        jsonschema.validate(data.get("json_object", {}), schema.first().json_schema)
    except Exception:
        raise ProcessingException(
            description="The object submited is not validated by the schema.", code=400
        )
