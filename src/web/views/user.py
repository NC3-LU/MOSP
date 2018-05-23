from flask import Blueprint, render_template
from flask_login import login_required

#from web.models import User

user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


@user_bp.route('/schemas', methods=['GET'])
@login_required
def me():
    return render_template('user_schemas.html')
