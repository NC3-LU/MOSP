from flask import Blueprint, render_template, redirect, url_for, flash, \
                  request, abort
from flask_login import login_required, current_user

from bootstrap import db, application
from web.models import Schema

schema_bp = Blueprint('schema_bp', __name__, url_prefix='/schema')
schemas_bp = Blueprint('schemas_bp', __name__, url_prefix='/schemas')


@schemas_bp.route('/', methods=['GET'])
def list_shemas():
    """Return the page which will display the list of schemas."""
    return render_template('schemas.html')


@schema_bp.route('/<int:schema_id>', methods=['GET'])
def get(schema_id=None):
    """Return the schema given in parameter."""
    schema = Schema.query.filter(Schema.id == schema_id).first()
    if schema is None:
        abort(404)
    return render_template('schema.html', schema=schema)
