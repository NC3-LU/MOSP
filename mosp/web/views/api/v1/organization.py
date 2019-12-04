#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, manager

import models
from web.views.api.v1.common import url_prefix


blueprint_organization = manager.create_api_blueprint(
    models.Organization,
    max_results_per_page=1000,
    results_per_page=50,
    url_prefix=url_prefix,
    exclude_columns=['objects', 'schemas', 'users'],
    methods=['GET'])
