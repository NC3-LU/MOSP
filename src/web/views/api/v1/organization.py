#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, manager

from web import models
from web.views.api.v1 import processors
from web.views.api.v1.common import url_prefix


blueprint_organization = manager.create_api_blueprint(
    models.Organization,
    max_results_per_page=1000,
    results_per_page=10,
    url_prefix=url_prefix,
    exclude_columns=['objects', 'schemas', 'users'],
    methods=['GET'])
