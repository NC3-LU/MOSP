
import logging
from flask import Blueprint, current_app, render_template, flash, redirect, \
                  url_for
from flask_login import login_required, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink
from werkzeug import generate_password_hash
from flask_babel import gettext
from datetime import datetime, timedelta

from bootstrap import db
from web.views.common import admin_permission
from web import models
from web.forms import UserForm, OrganizationForm

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')


@admin_bp.route('/dashboard', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def dashboard():
    now = datetime.utcnow()
    on_week_ago = now - timedelta(weeks=1)
    four_weeks_ago = now - timedelta(weeks=4)
    active_users = models.User.query.filter(
                            models.User.last_seen >= on_week_ago)
    recent_objects = models.JsonObject.query.filter(
                            models.JsonObject.last_updated >= four_weeks_ago)
    return render_template('admin/dashboard.html', USERS=active_users,
                            OBJECTS=recent_objects)


#
# Users
#

@admin_bp.route('/users', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def list_users():
    users = {}
    users['Admins'] = models.User.query.filter(models.User.is_admin==True)
    users['Users'] = models.User.query.filter(models.User.is_admin==False)
    return render_template('admin/users.html', users=users)


@admin_bp.route('/user/create', methods=['GET'])
@admin_bp.route('/user/edit/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def form_user(user_id=None):
    """Return a form to create and edit a user."""
    action = "Add a user"
    head_titles = [action]
    form = UserForm()
    if user_id is None:
        return render_template('admin/edit_user.html', action=action,
                               head_titles=head_titles, form=form)

    user = models.User.query.filter(models.User.id == user_id).first()
    form = UserForm(obj=user)
    form.organizations.data = [organization.id for organization in user.organizations]
    action = "Edit user"
    head_titles = [action]
    head_titles.append(user.login)
    return render_template('admin/edit_user.html', action=action,
                           head_titles=head_titles,
                           form=form, user=user)


@admin_bp.route('/user/create', methods=['POST'])
@admin_bp.route('/user/edit/<int:user_id>', methods=['POST'])
@login_required
def process_user_form(user_id=None):
    """Edit a user."""
    form = UserForm()

    if not form.validate():
        return render_template('admin/edit_user.html', form=form)

    if user_id is not None:
        user = models.User.query.filter(models.User.id == user_id).first()
        # Linked organizations
        linked_organizations = []
        for organization_id in form.organizations.data:
            organization = models.Organization.query.filter(models.Organization.id == organization_id).first()
            linked_organizations.append(organization)
        user.organizations = linked_organizations
        del form.organizations
        form.populate_obj(user)
        if form.password.data:
            user.pwdhash = generate_password_hash(form.password.data)
        db.session.commit()
        flash(gettext('User %(user_login)s successfully updated.',
                user_login=form.login.data), 'success')
        return redirect(url_for('admin_bp.form_user', user_id=user.id))

    # Create a new user
    new_user = models.User(login=form.login.data,
                           public_profile=form.public_profile.data,
                           is_active=form.is_active.data,
                           is_admin=form.is_admin.data,
                           is_api=form.is_api.data,
                           pwdhash=generate_password_hash(form.password.data))
    # Linked organizations
    linked_organizations = []
    for organization_id in form.organizations.data:
        organization = models.Organization.query.filter(models.Organization.id == organization_id).first()
        linked_organizations.append(organization)
    new_user.organizations.extend(linked_organizations)
    del form.organizations
    db.session.add(new_user)
    db.session.commit()
    flash(gettext('User %(user_login)s successfully created.',
            user_login=new_user.login), 'success')

    return redirect(url_for('admin_bp.form_user', user_id=new_user.id))


@admin_bp.route('/user/toggle/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def toggle_user(user_id=None):
    """Activate/deactivate a user."""
    user = models.User.query.filter(models.User.id == user_id).first()
    if user.id == current_user.id:
        flash(gettext('You can not do this change to your own user.'), 'danger')
    else:
        user.is_active = not user.is_active
        db.session.commit()
        flash(gettext('User {status}.').format(status=gettext('activated') if user.is_active else gettext('deactivated')), 'success')
    return redirect(url_for('admin_bp.list_users'))


@admin_bp.route('/user/delete/<int:user_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def delete_user(user_id=None):
    """Delete a user."""
    user = models.User.query.filter(models.User.id == user_id).first()
    if user.id == current_user.id:
        flash(gettext('You can not delete your own user.'), 'danger')
    else:
        db.session.delete(user)
        db.session.commit()
        flash(gettext('User deleted.'), 'success')
    return redirect(url_for('admin_bp.list_users'))

#
# Organizations
#

@admin_bp.route('/organizations', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def list_organizations():
    organizations = models.Organization.query.all()
    return render_template('admin/organizations.html',
                            organizations=organizations)


@admin_bp.route('/organization/create', methods=['GET'])
@admin_bp.route('/organization/edit/<int:organization_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def form_organization(organization_id=None):
    """Return a form to create and edit a user."""
    action = "Add an organization"
    head_titles = [action]
    form = OrganizationForm()
    if organization_id is None:
        return render_template('admin/edit_organization.html', action=action,
                               head_titles=head_titles, form=form)

    organization = models.Organization.query. \
                    filter(models.Organization.id == organization_id).first()
    form = OrganizationForm(obj=organization)
    form.users.data = [user.id for user in organization.users]
    action = "Edit an organization"
    head_titles = [action]
    head_titles.append(organization.name)
    return render_template('admin/edit_organization.html', action=action,
                           head_titles=head_titles,
                           form=form, organization=organization)


@admin_bp.route('/organization/create', methods=['POST'])
@admin_bp.route('/organization/edit/<int:organization_id>', methods=['POST'])
@login_required
def process_organization_form(organization_id=None):
    """Edit an organization."""
    form = OrganizationForm()

    if not form.validate():
        return render_template('admin/edit_organization.html', form=form)

    # Edit an existing organization
    if organization_id is not None:
        organization = models.Organization.query.filter(models.Organization.id == organization_id).first()
        # Members
        new_members = []
        for user_id in form.users.data:
            user = models.User.query.filter(models.User.id == user_id).first()
            new_members.append(user)
        organization.users = new_members
        del form.users
        form.populate_obj(organization)
        db.session.commit()
        flash(gettext('Organization %(org_name)s successfully updated.',
                org_name=form.name.data), 'success')
        return redirect(url_for('admin_bp.form_organization',
                                organization_id=organization.id))

    # Create a new organization
    new_organization = models.Organization(name=form.name.data,
                           description=form.description.data,
                           organization_type=form.organization_type.data)
    new_members = []
    for user_id in form.users.data:
        user = models.User.query.filter(models.User.id == user_id).first()
        new_members.append(user)
    new_organization.users = new_members
    del form.users
    db.session.add(new_organization)
    db.session.commit()
    flash(gettext('Organization %(org_name)s successfully created.',
            org_name=new_organization.name), 'success')

    return redirect(url_for('admin_bp.form_organization',
                            organization_id=new_organization.id))


@admin_bp.route('/organization/delete/<int:organization_id>', methods=['GET'])
@login_required
@admin_permission.require(http_exception=403)
def delete_organization(organization_id=None):
    """Delete an organization."""
    organization = models.Organization.query. \
                    filter(models.Organization.id == organization_id).first()
    db.session.delete(organization)
    db.session.commit()
    flash(gettext('Organization deleted.'), 'success')
    return redirect(url_for('admin_bp.list_organizations'))


# Flask-Admin views

class SecureView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


menu_link_back_home = MenuLink(name='Home',
                                    url='/')
admin_flask = Admin(current_app,
                    name='Management of data',
                    template_mode='bootstrap3',
                    index_view=CustomAdminIndexView(
                        name='Home',
                        url='/admin'
                    ))
admin_flask.add_view(SecureView(models.User, db.session))
admin_flask.add_view(SecureView(models.Organization, db.session))
admin_flask.add_view(SecureView(models.Schema, db.session))
admin_flask.add_view(SecureView(models.JsonObject, db.session))
admin_flask.add_view(SecureView(models.License, db.session))
admin_flask.add_link(menu_link_back_home)
