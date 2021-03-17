#! /usr/bin/env python
# -*- coding: utf-8 -*-

from mosp.bootstrap import manager, application

from mosp.models import Schema
from mosp.web.views.api.v1_1.common import url_prefix


def pre_get_many(search_params=None, **kw):
    order_by = [{"field": "last_updated", "direction": "desc"}]
    if "order_by" not in search_params:
        search_params["order_by"] = []
    search_params["order_by"].extend(order_by)


blueprint_schema = manager.create_api_blueprint(
    'SchemaAPI',
    Schema,
    url_prefix=url_prefix,
    exclude=["creator", "creator_id", "objects"],
    additional_attributes=["organization"],
    methods=["GET"],
    preprocessors=dict(GET_MANY=[pre_get_many]),
)
print('blueprint_schema')

# application.register_blueprint(blueprint_schema)
