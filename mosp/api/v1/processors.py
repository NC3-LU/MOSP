#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from flask import request
from flask_login import current_user
from flask_restless import ProcessingException

from mosp.models import User, JsonObject
from mosp.views.common import login_user_bundle
from mosp.api.common import check_submitted_object

logger = logging.getLogger(__name__)


def auth_func(*args, **kw):
    """
    Pre-processor used to check if a user is authenticated.
    """
    if current_user.is_authenticated:
        return

    user = None
    if request.headers.get("Authorization", False):
        token = request.headers.get("Authorization").split(" ")[1]
        user = User.query.filter(User.apikey == token).first()

    if request.authorization:
        user = User.query.filter(User.login == request.authorization.username).first()
        if user and not user.check_password(request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user", code=401)

    if not user:
        raise ProcessingException("Couldn't authenticate your user", code=401)
    if not user.is_active:
        raise ProcessingException("Couldn't authenticate your user", code=401)

    login_user_bundle(user)


def check_single_object_edit_permission(instance_id, data):
    """Pre-processor to edit a single object."""
    if not current_user.is_authenticated:
        raise ProcessingException(description="Not authenticated!", code=401)

    json_object = JsonObject.query.filter(JsonObject.id == instance_id).first()
    if json_object:
        # set the values requires by check_submitted_object()
        data["schema_id"] = json_object.schema.id
        data["org_id"] = json_object.organization.id
        data["creator_id"] = (
            json_object.creator.id if json_object.creator.id else current_user.id
        )
    else:
        raise ProcessingException(description="Unknown object", code=401)
    try:
        check_submitted_object(data)
    except Exception as e:
        raise (e)


def create_new_version_before_update(instance_id, data):
    json_object = JsonObject.query.filter(JsonObject.id == instance_id).first()
    new_version = json_object.create_new_version()
    json_object.editor_id = current_user.id


def check_object_creation_permission(data):
    """Check if the user is authenticated and set the creator_id."""
    if not current_user.is_authenticated:
        raise ProcessingException(description="Not authenticated!", code=401)

    data["creator_id"] = current_user.id
    check_submitted_object(data)
