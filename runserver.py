#! /usr/bin/env python
# -*- coding: utf-8 -*-

from mosp.bootstrap import application
from mosp import commands


def register_commands(app):
    """Register Click commands."""
    app.cli.add_command(commands.uml_graph)
    app.cli.add_command(commands.db_empty)
    app.cli.add_command(commands.db_create)
    app.cli.add_command(commands.db_init)
    app.cli.add_command(commands.import_licenses_from_spdx)
    app.cli.add_command(commands.create_admin)
    app.cli.add_command(commands.create_user)


with application.app_context():

    from mosp import views
    import mosp.api.v1 as api_v1
    import mosp.api.v2 as api_v2

    application.register_blueprint(views.schema_bp)
    application.register_blueprint(views.schemas_bp)
    application.register_blueprint(views.object_bp)
    application.register_blueprint(views.objects_bp)
    application.register_blueprint(views.admin_bp)
    application.register_blueprint(views.user_bp)
    application.register_blueprint(views.organization_bp)
    application.register_blueprint(views.organizations_bp)
    application.register_blueprint(views.stats_bp)
    application.register_blueprint(views.collection_bp)
    application.register_blueprint(views.collections_bp)

    # API v1
    application.register_blueprint(api_v1.blueprint_organization)
    application.register_blueprint(api_v1.blueprint_schema)
    application.register_blueprint(api_v1.blueprint_object)

    # API v2
    application.register_blueprint(api_v2.apiv2_blueprint)

    register_commands(application)


if __name__ == "__main__":
    application.run(host=application.config["HOST"], port=application.config["PORT"])
