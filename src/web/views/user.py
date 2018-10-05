from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug import generate_password_hash
from flask_babel import gettext

from bootstrap import db
from web.models import User
from web.forms import ProfileForm


user_bp = Blueprint('user_bp', __name__, url_prefix='/user')


@user_bp.route('/<string:login>', methods=['GET'])
def get(login=None):
    """Return the user given in parameter with the objects created by this
    user."""
    user = User.query.filter(User.login == login).first()
    if user is None:
        abort(404)
    return render_template('user.html', user=user)


@user_bp.route('/schemas', methods=['GET'])
@login_required
def schemas():
    """Displays the schemas of the currently logged user."""
    return render_template('user_schemas.html')


@user_bp.route('/profile', methods=['GET'])
@login_required
def form():
    """Retruns the fom to edit a user."""
    user = User.query.filter(User.id == current_user.id).first()
    form = ProfileForm(obj=user)
    form.populate_obj(current_user)
    action = "Edit user"
    head_titles = [action]
    head_titles.append(user.login)
    return render_template('edit_user.html', action=action,
                           head_titles=head_titles,
                           form=form, user=user)


@user_bp.route('/profile', methods=['POST'])
@login_required
def process_form():
    """Process the form for the user edition."""
    form = ProfileForm()

    if not form.validate():
        return render_template('edit_user.html', form=form)

    user = User.query.filter(User.id == current_user.id).first()
    form.populate_obj(user)
    if form.password.data:
        user.pwdhash = generate_password_hash(form.password.data)
    db.session.commit()
    flash(gettext('User %(user_login)s successfully updated.',
            user_login=form.login.data), 'success')
    return redirect(url_for('admin_bp.form_user', user_id=user.id))
