import logging
import sys

from flask import current_app
from flask import flash
from flask import redirect
from flask import render_template
from flask import url_for
from flask_babel import gettext

from mosp import __version__
from mosp.lib.collections_utils import generate_collections_atom_feed
from mosp.lib.objects_utils import generate_objects_atom_feed
from mosp.lib.schemas_utils import generate_schemas_atom_feed
from mosp.models import JsonObject
from mosp.models import Organization
from mosp.models import Schema
from mosp.models import User

logger = logging.getLogger(__name__)


@current_app.errorhandler(401)
def authentication_required(error):
    flash(gettext("Authentication required."), "info")
    return redirect(url_for("login"))


@current_app.errorhandler(403)
def authentication_failed(error):
    flash(gettext("Forbidden."), "danger")
    return redirect(url_for("login"))


@current_app.errorhandler(404)
def page_not_found(error):
    return render_template("errors/404.html"), 404


@current_app.errorhandler(500)
def internal_server_error_500(error):
    return render_template("errors/500.html"), 500


@current_app.errorhandler(503)
def internal_server_error_503(error):
    return render_template("errors/503.html"), 503


@current_app.errorhandler(AssertionError)
def handle_sqlalchemy_assertion_error(error):
    return error.args[0], 400


@current_app.route("/", methods=["GET"])
def index():
    """Home page."""
    return render_template(
        "index.html",
        nb_objects=JsonObject.query.count(),
        nb_organizations=Organization.query.count(),
    )


@current_app.route("/about", methods=["GET"])
def about():
    """About page."""
    return render_template("about.html")


@current_app.route("/about/more", methods=["GET"])
def about_more():
    """Returns some details about the current MOSP instance (version of MOSP
    version of Python, number of objects, etc.)
    """
    version = __version__.split("-")
    if len(version) == 1:
        mosp_version = version[0]
        version_url = "https://github.com/NC3-LU/MOSP/releases/tag/{}".format(
            version[0]
        )
    else:
        mosp_version = f"{version[0]} - {version[2][1:]}"
        version_url = f"https://github.com/NC3-LU/MOSP/commits/{version[2][1:]}"
    return render_template(
        "about_more.html",
        mosp_version=mosp_version,
        version_url=version_url,
        python_version="{}.{}.{}".format(*sys.version_info[:3]),
        nb_objects=JsonObject.query.count(),
        nb_schemas=Schema.query.count(),
        nb_organizations=Organization.query.count(),
        nb_users=User.query.count(),
    )


@current_app.route("/help", methods=["GET"])
def help():
    """Documentation page."""
    return render_template("help.html")


@current_app.route("/terms", methods=["GET"])
def terms():
    """Terms page."""
    return render_template("terms.html")


@current_app.route("/humans.txt", methods=["GET"])
def humans():
    """Human dot txt page."""
    return render_template("humans.txt"), 200, {"Content-Type": "text/plain"}


@current_app.route("/robots.txt", methods=["GET"])
def robots():
    """Robots dot txt page."""
    return render_template("robots.txt"), 200, {"Content-Type": "text/plain"}


@current_app.route("/.well-known/security.txt", methods=["GET"])
def security():
    """security dot txt page (RFC 9116)."""
    return render_template("security.txt"), 200, {"Content-Type": "text/plain"}


@current_app.route("/objects.atom", methods=["GET"])
def objects_atom():
    """Returns an ATOM feed with the recent updated objects."""
    atomfeed = generate_objects_atom_feed()
    return atomfeed


@current_app.route("/schemas.atom", methods=["GET"])
def schemas_atom():
    """Returns an ATOM feed with the recent updated schemas."""
    atomfeed = generate_schemas_atom_feed()
    return atomfeed


@current_app.route("/collections.atom", methods=["GET"])
def collections_atom():
    """Returns an ATOM feed with the recent updated collections."""
    atomfeed = generate_collections_atom_feed()
    return atomfeed
