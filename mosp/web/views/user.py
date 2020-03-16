from flask import Blueprint, render_template, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from flask_babel import gettext
from flask_paginate import Pagination, get_page_args

from mosp.bootstrap import db
from mosp.models import User, JsonObject
from mosp.web.forms import ProfileForm


user_bp = Blueprint("user_bp", __name__, url_prefix="/user")


@user_bp.route("/<string:login>", defaults={"per_page": "10"}, methods=["GET"])
def get(per_page, login=None):
    """Return the user given in parameter with the objects created by this
    user."""
    user = User.query.filter(User.login == login).first()
    if user is None:
        abort(404)
    # Pagination on objects created by the user
    query = JsonObject.query.filter(JsonObject.creator_id == user.id)
    page, per_page, offset = get_page_args()
    pagination = Pagination(
        page=page,
        total=query.count(),
        css_framework="bootstrap4",
        search=False,
        record_name="objects",
        per_page=per_page,
    )
    return render_template(
        "user.html",
        user=user,
        pagination=pagination,
        objects=query.offset(offset).limit(per_page),
    )


@user_bp.route("/schemas", methods=["GET"])
@login_required
def schemas():
    """Displays the schemas of the currently logged user."""
    return render_template("user_schemas.html", user=current_user)


@user_bp.route("/profile", methods=["GET"])
@login_required
def form():
    """Retruns the fom to edit a user."""
    user = User.query.filter(User.id == current_user.id).first()
    form = ProfileForm(obj=user)
    form.populate_obj(current_user)
    action = gettext("Edit user")
    head_titles = [action]
    head_titles.append(user.login)
    return render_template(
        "edit_user.html", action=action, head_titles=head_titles, form=form, user=user
    )


@user_bp.route("/profile", methods=["POST"])
@login_required
def process_form():
    """Process the form for the user edition."""
    form = ProfileForm()

    if not form.validate():
        return render_template("edit_user.html", form=form)

    user = User.query.filter(User.id == current_user.id).first()
    form.populate_obj(user)
    if form.password.data:
        user.pwdhash = generate_password_hash(form.password.data)
    db.session.commit()
    flash(
        gettext(
            "User %(user_login)s successfully updated.", user_login=form.login.data
        ),
        "success",
    )
    return redirect(url_for("admin_bp.form_user", user_id=user.id))


@user_bp.route("/generate_apikey", methods=["GET"])
@login_required
def generate_apikey():
    """Generate an API key for a user."""
    user = User.query.filter(User.id == current_user.id).first()
    if user is None:
        abort(404)
    user.generate_apikey()
    db.session.commit()
    flash(gettext("New API key generated."), "success")
    return redirect(url_for("user_bp.form"))


@user_bp.route("/delete_account", methods=["GET"])
@login_required
def delete_account():
    """Delete the account of a user."""
    user = User.query.filter(User.id == current_user.id).first()
    if user is None:
        abort(404)
    db.session.delete(user)
    db.session.commit()
    flash(gettext("Account deleted."), "success")
    return redirect(url_for("index"))
