import sys
import json
import logging
from datetime import timezone
from flask import render_template, url_for, redirect, current_app, flash
from flask_babel import gettext
from feedgen.feed import FeedGenerator

from mosp import __version__
from mosp.models import JsonObject, Organization, User, Schema
from mosp.bootstrap import application

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
        version_url = "https://github.com/CASES-LU/MOSP/releases/tag/{}".format(
            version[0]
        )
    else:
        mosp_version = "{} - {}".format(version[0], version[2][1:])
        version_url = "https://github.com/CASES-LU/MOSP/commits/{}".format(
            version[2][1:]
        )
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


@current_app.route("/human.txt", methods=["GET"])
def human():
    """Human dot txt page."""
    return render_template("human.txt"), 200, {"Content-Type": "text/plain"}


@current_app.route("/objects.atom", methods=["GET"])
def objects_atom():
    """Generates an ATOM feed with the recent updated objects."""
    recent_objects = JsonObject.query.order_by(JsonObject.last_updated.desc()).limit(50)
    fg = FeedGenerator()
    fg.id(url_for("objects_atom", _external=True))
    fg.title("Recent objects published on MOSP")
    # fg.subtitle("")
    fg.link(href=application.config["INSTANCE_URL"], rel="self")
    fg.author(
        {
            "name": application.config["ADMIN_URL"],
            "email": application.config["ADMIN_EMAIL"],
        }
    )
    fg.language("en")
    for recent_object in recent_objects:
        fe = fg.add_entry()
        fe.id(
            url_for(
                "object_bp.get_json_object", object_id=recent_object.id, _external=True
            )
        )
        fe.title(recent_object.name)
        fe.description(recent_object.description)
        fe.author({"name": recent_object.organization.name})
        fe.content(
            json.dumps(
                recent_object.json_object,
                sort_keys=True,
                indent=4,
                separators=(",", ": "),
            )
        )
        fe.published(recent_object.last_updated.replace(tzinfo=timezone.utc))
        fe.link(
            href=url_for(
                "object_bp.get_json_object", object_id=recent_object.id, _external=True
            )
        )
    atomfeed = fg.atom_str(pretty=True)
    return atomfeed
