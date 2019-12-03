#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, populate_g

with application.app_context():
    populate_g()

    from web import views
    application.register_blueprint(views.schema_bp)
    application.register_blueprint(views.schemas_bp)
    application.register_blueprint(views.object_bp)
    application.register_blueprint(views.objects_bp)
    application.register_blueprint(views.admin_bp)
    application.register_blueprint(views.user_bp)
    application.register_blueprint(views.organization_bp)
    application.register_blueprint(views.organizations_bp)

    # API v1
    application.register_blueprint(views.api.v1.blueprint_organization)
    application.register_blueprint(views.api.v1.blueprint_schema)
    application.register_blueprint(views.api.v1.blueprint_object)


if __name__ == '__main__':
    application.run(host=application.config['HOST'],
                    port=application.config['PORT'])
