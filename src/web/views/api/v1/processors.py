#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from flask import request
from flask_login import current_user
from flask_restless import ProcessingException
from jsonschema import validate

from web.views.common import login_user_bundle
from web.models import User, Schema

logger = logging.getLogger(__name__)

def auth_func(*args, **kw):
    if request.authorization:
        user = User.query.filter(User.login == request.authorization.username).first()
        if not user:
            raise ProcessingException("Couldn't authenticate your user",
                                      code=401)
        if not user.check_password(request.authorization.password):
            raise ProcessingException("Couldn't authenticate your user",
                                      code=401)
        if not user.is_active:
            raise ProcessingException("Couldn't authenticate your user", code=401)
        login_user_bundle(user)
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated!', code=401)



def check_object_edit_permission(data):
    if not current_user.is_authenticated:
        raise ProcessingException(description='Not authenticated!', code=401)

    schema_id = data.get('schema_id', None)
    org_id = data.get('org_id', None)

    data['creator_id'] = current_user.id

    if org_id is None:
        raise ProcessingException(description='You must provide the id of an organization.', code=400)

    if org_id not in [org.id for org in current_user.organizations]:
        raise ProcessingException(description='You are not allowed to create/edit object from this organization.', code=400)

    if schema_id is None:
        raise ProcessingException(description='You must provide the id of a schema.', code=400)

    schema = Schema.query.filter(Schema.id == schema_id).first()

    try:
        validate(data.get('json_object', {}), schema.json_schema)
    except Exception as e:
        print(e)
        raise ProcessingException(description='The object submited is not validated by the schema.', code=400)
