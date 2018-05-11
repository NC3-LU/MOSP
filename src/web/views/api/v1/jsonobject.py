#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask_login import current_user
from bootstrap import application, manager

from web import models
from web.views.api.v1 import processors
from web.views.api.v1.common import url_prefix


def pre_get_many(search_params=None, **kw):
    order_by = [{"field":"last_updated", "direction":"desc"}]
    if 'order_by' not in search_params:
        search_params['order_by'] = []
    search_params['order_by'].extend(order_by)

    if not current_user.is_authenticated:
        filters = [dict(name='is_public', op='eq', val=True)]
        if 'filters' not in search_params:
            search_params['filters'] = []
        search_params['filters'].extend(filters)

    if current_user.is_authenticated and not current_user.is_admin:
        # filters = [dict(name='is_public', op='eq', val=True)]
        filters = [{
                    "or":  [dict(name='is_public', op='eq', val=True)],
                            "and":
                                [dict(name='org_id', op='in', val=[org.id for org in current_user.organizations]),
                                dict(name='is_public', op='eq', val=False)]

                   }]


        if 'filters' not in search_params:
            search_params['filters'] = []
        search_params['filters'].extend(filters)


blueprint_object = manager.create_api_blueprint(
    models.JsonObject,
    url_prefix=url_prefix,
    methods=['GET', 'POST', 'PUT', 'DELETE'],
    preprocessors=dict(
        GET_MANY=[pre_get_many],
        POST=[processors.auth_func],
        PUT=[processors.auth_func],
        DELETE=[processors.auth_func]))
