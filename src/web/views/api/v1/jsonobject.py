#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask_login import current_user
from bootstrap import application, manager

from web import models
from web.views.api.v1 import processors
from web.views.api.v1.common import url_prefix


def pre_get_many(search_params=None, **kw):
    """Filter for HTTP GET many requests. Checks if a authenticated user
    has appropriate rights to see an object."""
    order_by = [{"field":"last_updated", "direction":"desc"}]
    if 'order_by' not in search_params:
        search_params['order_by'] = []
    search_params['order_by'].extend(order_by)


blueprint_object = manager.create_api_blueprint(
    models.JsonObject,
    max_results_per_page=5000,
    results_per_page=10,
    url_prefix=url_prefix,
    methods=['GET', 'POST', 'PUT'],
    exclude_columns=['creator', 'creator_id'],
    preprocessors=dict(
        GET_MANY=[pre_get_many],
        POST=[processors.auth_func, processors.check_object_edit_permission],
        PUT=[processors.auth_func, processors.check_object_edit_permission],
        PUT_SINGLE=[processors.auth_func,
                        processors.check_single_object_edit_permission]))
