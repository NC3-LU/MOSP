#! /usr/bin/env python
# -*- coding: utf-8 -*-

from mosp.bootstrap import manager, application

from mosp.models import Organization
from mosp.web.views.api.v1.common import url_prefix


blueprint_organization = manager.create_api_blueprint(
    'organizationapi',
    model=Organization,
    url_prefix=url_prefix,
    methods=["GET"],
)
print('blueprint_organization')

# application.register_blueprint(blueprint_organization)
