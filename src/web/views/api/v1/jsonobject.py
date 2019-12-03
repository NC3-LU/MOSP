#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import manager

from web import models
from web.views.api.v1 import processors
from web.views.api.v1.common import url_prefix


def pre_get_many(search_params=None, **kw):
    """Filter for HTTP GET many requests. Checks if a authenticated user
    has appropriate rights to see an object."""
    order_by = [{"field": "last_updated", "direction": "desc"}]
    if 'order_by' not in search_params:
        search_params['order_by'] = []
    search_params['order_by'].extend(order_by)
    search_params['exclude'] = ["description"]


def get_many_postprocessor(result=None, search_params=None, **kw):
    """Accepts two arguments, `result`, which is the dictionary
    representation of the JSON response which will be returned to the
    client, and `search_params`, which is a dictionary containing the
    search parameters for the request (that produced the specified
    `result`).

    It would be better to filter these columns with a preprocessor.
    """
    def pop_object(elem):
        # elem.pop('json_object')
        elem.pop('schema')
        elem.pop('referred_to_by')
        elem.pop('refers_to')
        return elem
    list(map(lambda elem: pop_object(elem), result['objects']))


blueprint_object = manager.create_api_blueprint(
    models.JsonObject,
    max_results_per_page=5000,
    results_per_page=10,
    url_prefix=url_prefix,
    methods=['GET', 'POST', 'PUT'],
    exclude_columns=['creator', 'creator_id'],
    postprocessors=dict(GET_MANY=[get_many_postprocessor]),
    preprocessors=dict(
        GET_MANY=[pre_get_many],
        POST=[processors.auth_func, processors.check_object_creation_permission],
        PUT=[processors.auth_func, processors.check_single_object_edit_permission],
        PUT_SINGLE=[processors.auth_func,
                        processors.check_single_object_edit_permission]))
