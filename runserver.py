#! /usr/bin/env python
# -*- coding: utf-8 -*-

# MOSP - A platform for creating, editing and sharing JSON objects.
# Copyright (C) 2018-2022 Cédric Bonhomme - https://www.cedricbonhomme.org
# Copyright (C) 2018-2022 SMILE gie - securitymadein.lu
#
# For more information: https://github.com/CASES-LU/MOSP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

    # API v2
    application.register_blueprint(api_v2.apiv2_blueprint)

    register_commands(application)


if __name__ == "__main__":
    application.run(host=application.config["HOST"], port=application.config["PORT"])
