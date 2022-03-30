from flask import current_app
from flask_login import login_user
from flask_principal import Identity
from flask_principal import identity_changed
from flask_principal import Permission
from flask_principal import RoleNeed
from flask_principal import session_identity_loader

admin_role = RoleNeed("admin")
api_role = RoleNeed("api")

admin_permission = Permission(admin_role)
api_permission = Permission(api_role)


def login_user_bundle(user):
    login_user(user)
    identity_changed.send(current_app, identity=Identity(user.id))
    session_identity_loader()
