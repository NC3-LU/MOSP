from flask import Blueprint, render_template, abort

from web.models import Organization

organization_bp = Blueprint('organization_bp', __name__, url_prefix='/organization')
organizations_bp = Blueprint('organizations_bp', __name__, url_prefix='/organizations')


@organizations_bp.route('/', methods=['GET'])
def list_organizations():
    """Return the page which will display the list of organizations."""
    return render_template('organizations.html')


@organization_bp.route('/<int:organization_id>', methods=['GET'])
def get(organization_id=None):
    """Return the organization given in parameter."""
    org = Organization.query.filter(Organization.id == organization_id).first()
    if org is None:
        abort(404)
    return render_template('organization.html', organization=org)
