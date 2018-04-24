
import logging
from flask import Blueprint, current_app
from flask_login import login_required, current_user
from flask_admin import Admin, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.menu import MenuLink

from bootstrap import db
from web import models

logger = logging.getLogger(__name__)

admin_bp = Blueprint('admin_bp', __name__, url_prefix='/admin')



# Flask-Admin views

class SecureView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

class CustomAdminIndexView(AdminIndexView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin


menu_link_back_dashboard = MenuLink(name='Dashboard',
                                    url='/admin/dashboard')
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
# admin_flask.add_view(SecureView(models.Object, db.session))
admin_flask.add_link(menu_link_back_dashboard)
