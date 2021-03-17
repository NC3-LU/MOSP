#! /usr/bin/env python
# -*- coding: utf-8 -*-

from mosp.bootstrap import manager, application

from mosp.models import Organization
from mosp.web.views.api.v1_1.common import url_prefix


blueprint_organization = manager.create_api_blueprint(
    'organizationapi',
    model=Organization,
    url_prefix=url_prefix,
    exclude=["objects", "schemas", "users"],
    methods=["GET"],
)
