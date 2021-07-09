from flask import Blueprint, render_template
from flask_restx import Api

from mosp.bootstrap import application


apiv2_blueprint = Blueprint("apiv2", __name__, url_prefix="/api/v2")


def setup_api(application):
    authorizations = {
        "apikey": {
            "type": "apiKey",
            "in": "header",
            "name": "X-API-KEY",
        }
    }

    api = Api(
        apiv2_blueprint,
        title="MONARC Objects Sharing Platform",
        version="2.0",
        description="API v2 of the MONARC Objects Sharing Platform.",
        license="GNU Affero General Public License version 3",
        license_url="https://www.gnu.org/licenses/agpl-3.0.html",
        doc="/",
        security="apikey",
        authorizations=authorizations,
        contact_email=application.config["ADMIN_EMAIL"],
        contact_url=application.config["ADMIN_URL"],
    )

    @api.documentation
    def custom_ui():
        return render_template(
            "swagger-ui.html",
            title=api.title,
            specs_url="{}/api/v2/swagger.json".format(
                application.config["INSTANCE_URL"]
            ),
        )

    from mosp.api.v2 import object, organization, schema, user

    api.add_namespace(object.object_ns, path="/object")
    api.add_namespace(organization.organization_ns, path="/organization")
    api.add_namespace(schema.schema_ns, path="/schema")
    api.add_namespace(user.user_ns, path="/user")

    return api


api = setup_api(application)
