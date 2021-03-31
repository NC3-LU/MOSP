import logging

import sqlalchemy
from datetime import datetime
from flask import render_template, session, url_for, redirect, current_app, flash
from flask_login import LoginManager, logout_user, login_required, current_user
from flask_principal import (
    Principal,
    AnonymousIdentity,
    UserNeed,
    identity_changed,
    identity_loaded,
    session_identity_loader,
)
from werkzeug.security import generate_password_hash
from flask_babel import lazy_gettext, gettext

from mosp.bootstrap import db, application
from mosp.models import User
from mosp.views.common import admin_role, api_role, login_user_bundle
from mosp.forms import SigninForm, SignupForm
from mosp.notifications import notifications

Principal(current_app)
# Create a permission with a single Need, in this case a RoleNeed.

login_manager = LoginManager()
login_manager.init_app(current_app)
login_manager.login_view = "login"
login_manager.login_message = lazy_gettext("Please log in to access this page.")
login_manager.login_message_category = "info"

logger = logging.getLogger(__name__)


@identity_loaded.connect_via(current_app._get_current_object())
def on_identity_loaded(sender, identity):
    # Set the identity user object
    identity.user = current_user

    # Add the UserNeed to the identity
    if current_user.is_authenticated:
        identity.provides.add(UserNeed(current_user.id))
        if current_user.is_admin:
            identity.provides.add(admin_role)
        if current_user.is_api:
            identity.provides.add(api_role)


@login_manager.user_loader
def load_user(user_id):
    return User.query.filter(User.id == user_id, User.is_active == True).first()


@current_app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@current_app.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = SigninForm()
    if form.validate_on_submit():
        login_user_bundle(form.user)
        return redirect(form.redirect_target or url_for("user_bp.schemas"))
    return render_template("login.html", form=form)


@current_app.route("/logout")
@login_required
def logout():
    # Remove the user information from the session
    logout_user()

    # Remove session keys set by Flask-Principal
    for key in ("identity.name", "identity.auth_type"):
        session.pop(key, None)

    # Tell Flask-Principal the user is anonymous
    identity_changed.send(current_app, identity=AnonymousIdentity())
    session_identity_loader()

    return redirect(url_for("login"))


@current_app.route("/signup", methods=["GET", "POST"])
def signup():
    if not application.config["SELF_REGISTRATION"]:
        flash(gettext("Self-registration is disabled."), "warning")
        return redirect(url_for("index"))
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    form = SignupForm()
    if form.validate_on_submit():
        try:
            new_user = User(
                login=form.login.data,
                email=form.email.data,
                pwdhash=generate_password_hash(form.password.data),
                is_active=False,
                is_admin=False,
            )
            db.session.add(new_user)
            db.session.commit()
        except sqlalchemy.exc.IntegrityError:
            db.session.rollback()

        # Send the confirmation email
        try:
            notifications.confirm_account(new_user)
        except Exception as error:
            flash(
                gettext(
                    "Problem while sending activation email: %(error)s", error=error
                ),
                "danger",
            )

        flash(
            gettext("Your account has been created. " "Check your mail to confirm it."),
            "success",
        )

        return redirect(url_for("index"))

    return render_template("signup.html", form=form)
