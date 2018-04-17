
from flask import current_app
from flask_login import login_user
from flask_principal import (Identity, Permission, RoleNeed,
                                 session_identity_loader, identity_changed)

admin_role = RoleNeed('admin')
api_role = RoleNeed('api')

admin_permission = Permission(admin_role)
api_permission = Permission(api_role)


def login_user_bundle(user):
    login_user(user)
    identity_changed.send(current_app, identity=Identity(user.id))
    session_identity_loader()
    # TODO: set last_seen
