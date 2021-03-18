#! /usr/bin/env python
# -*- coding: utf-8 -*-

from mosp.bootstrap import manager

from mosp.models import Schema
from mosp.web.api.v1.common import url_prefix


def pre_get_many(search_params=None, **kw):
    order_by = [{"field": "last_updated", "direction": "desc"}]
    if "order_by" not in search_params:
        search_params["order_by"] = []
    search_params["order_by"].extend(order_by)


blueprint_schema = manager.create_api_blueprint(
    Schema,
    max_results_per_page=1000,
    results_per_page=10,
    url_prefix=url_prefix,
    methods=["GET"],
    exclude_columns=["creator", "creator_id", "objects"],
    preprocessors=dict(GET_MANY=[pre_get_many]),
)
