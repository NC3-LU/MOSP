#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, manager

from web import models
from web.views.api.v1 import processors
from web.views.api.v1.common import url_prefix


blueprint_organization = manager.create_api_blueprint(
    models.Organization,
    url_prefix=url_prefix,
    methods=['GET', 'POST', 'PUT', 'DELETE'],
    preprocessors=dict(
        POST=[processors.auth_func],
        PUT=[processors.auth_func],
        DELETE=[processors.auth_func]))
