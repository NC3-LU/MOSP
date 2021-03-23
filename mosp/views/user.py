from flask import Blueprint, render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user
from werkzeug.security import generate_password_hash
from flask_babel import gettext
from flask_paginate import Pagination, get_page_args

from mosp.bootstrap import db
from mosp.models import User, JsonObject
from mosp.forms import (
    ProfileForm,
    AccountRecoveryForm,
    AccountRecoveryNewPasswordForm,
)
from mosp.lib.user_utils import confirm_token
from mosp.notifications import notifications


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


#
# Account revocery
#


@user_bp.route("/account_recovery", methods=["GET", "POST"])
def account_recovery():
    """Returns a form for the account recovery.
    The user will have to provide the login of the account to recover. It can
    not be done via email address since an email address is not unique.
    """
    form = AccountRecoveryForm()
    if request.method == "GET":
        return render_template("account_recovery.html", form=form)
    else:
        user = User.query.filter(User.login == form.login.data).first()
        if user is None:
            flash(
                gettext("This user does not exist."),
                "danger",
            )
            return redirect(url_for("index"))

        # Send the recovery email with the temporary token
        try:
            notifications.account_recovery(user)
        except Exception as error:
            flash(
                gettext(
                    "Problem while sending activation email: %(error)s", error=error
                ),
                "danger",
            )
            return redirect(url_for("index"))

        flash(gettext("An email with a recovery link has been sent to you."), "success")

    return redirect(url_for("index"))


@user_bp.route("/confirm_account/<string:token>", methods=["GET", "POST"])
def confirm_account(token=None):
    """
    Confirm the account of a user with the token that the user has received
    previously by email.
    """
    # Check the token
    user, login = None, None
    if token != "":
        login = confirm_token(token)
    if login:
        user = User.query.filter(User.login == login).first()
    if user is None:
        flash(gettext("Impossible to activate this account."), "danger")
        return redirect(url_for("login"))

    # Management of the Web form
    form = AccountRecoveryNewPasswordForm()

    if request.method == "GET":
        # Asks the user to provide a new password, in the case the token is
        # valid
        if user is not None:
            return render_template("account_recovery_set_password.html", form=form)
        else:
            flash(gettext("Impossible to activate this account."), "danger")
    else:
        # Update the password of the user (if the token is valid and if the
        # two passwards are equal)
        if form.password1.data == form.password2.data:
            user.pwdhash = generate_password_hash(form.password1.data)
            user.is_active = True
            db.session.add(user)
            db.session.commit()
            flash(gettext("Your password has been updated."), "success")
        else:
            flash(gettext("Password must be the same."), "danger")
            return render_template("account_recovery_set_password.html", form=form)

    return redirect(url_for("login"))
