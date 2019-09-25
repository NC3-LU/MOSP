import sys
import logging
from flask import render_template, url_for, redirect, current_app, flash
from flask_login import login_required
from flask_babel import gettext

from web import __version__
from web.models import JsonObject, Organization, User, Schema

logger = logging.getLogger(__name__)


@current_app.errorhandler(401)
def authentication_required(error):
    flash(gettext('Authentication required.'), 'info')
    return redirect(url_for('login'))


@current_app.errorhandler(403)
def authentication_failed(error):
    flash(gettext('Forbidden.'), 'danger')
    return redirect(url_for('login'))


@current_app.errorhandler(404)
def page_not_found(error):
    return render_template('errors/404.html'), 404


@current_app.errorhandler(500)
def internal_server_error(error):
    return render_template('errors/500.html'), 500


@current_app.errorhandler(503)
def internal_server_error(error):
    return render_template('errors/503.html'), 503


@current_app.errorhandler(AssertionError)
def handle_sqlalchemy_assertion_error(error):
    return error.args[0], 400


@current_app.route('/', methods=['GET'])
def index():
    """Home page."""
    return render_template('index.html')


@current_app.route('/about', methods=['GET'])
def about():
    """About page."""
    return render_template('about.html')


@current_app.route('/about/more', methods=['GET'])
def about_more():
    return render_template('about_more.html',
                mosp_version=__version__.split()[1],
                python_version="{}.{}.{}".format(*sys.version_info[:3]),
                nb_objects=JsonObject.query.count(),
                nb_schemas=Schema.query.count(),
                nb_organizations=Organization.query.count(),
                nb_users=User.query.count())


@current_app.route('/help', methods=['GET'])
def help():
    """Documentation page."""
    return render_template('help.html')


@current_app.route('/terms', methods=['GET'])
def terms():
    """Terms page."""
    return render_template('terms.html')


@current_app.route('/human.txt', methods=['GET'])
def human():
    """Human dot txt page."""
    return render_template('human.txt'), 200, {'Content-Type': 'text/plain'}
