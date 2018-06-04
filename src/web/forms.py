#! /usr/bin/env python
# -*- coding: utf-8 -*-

from flask import flash, url_for, redirect
from flask_wtf import FlaskForm
from wtforms import (TextField, TextAreaField, PasswordField, BooleanField,
                     SelectField, SubmitField, validators, HiddenField,
                     SelectMultipleField, HiddenField)
from flask_babel import lazy_gettext

from lib import misc_utils
from web.models import User, Organization


class RedirectForm(FlaskForm):
    """
    Secure back redirects with WTForms.
    """
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        FlaskForm.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = misc_utils.get_redirect_target() or ''

    def redirect(self, endpoint='services', **values):
        if misc_utils.is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = misc_utils.get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


class SigninForm(RedirectForm):
    """
    Sign in form.
    """
    login = TextField(lazy_gettext('Login'),
            [validators.Length(min=3, max=30),
            validators.Required(lazy_gettext('Please enter your login.'))])
    password = PasswordField(lazy_gettext('Password'),
            [validators.Required(lazy_gettext('Please enter your password.')),
             validators.Length(min=6, max=100)])
    submit = SubmitField(lazy_gettext('Log In'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = None

    def validate(self):
        validated = super().validate()
        user = User.query.filter(User.login == self.login.data).first()
        if not user:
            validated = False
        else:
            if not user.is_active:
                validated = False
            if not user.check_password(self.password.data):
                validated = False
            self.user = user
        if not validated:
            # intentionaly do not explain why it is impossible to login
            self.login.errors.append(lazy_gettext('Impossible to login.'))
        return validated


class AddObjectForm(FlaskForm):
    name = TextField("Name",
                    [validators.Required(lazy_gettext('Please enter a name'))])
    description = TextAreaField(lazy_gettext('Description'),
                    [validators.Required(lazy_gettext('Please enter a description'))])
    is_public = BooleanField(lazy_gettext('Public object'), default=True)
    schema_id = HiddenField(lazy_gettext('Validated by'))
    org_id = SelectField(lazy_gettext('Organization'),
                    [validators.Required(lazy_gettext('Please select an organization'))],
                    coerce=int)
    org_id.choices = [(0, '')]

    submit = SubmitField(lazy_gettext('Save'))


class SchemaForm(FlaskForm):
    name = TextField("Name",
                    [validators.Required(lazy_gettext('Please enter a name'))])
    description = TextAreaField(lazy_gettext('Description'),
                    [validators.Required(lazy_gettext('Please enter a description'))])
    json_schema = TextAreaField('JSON schema',
                    [validators.Required(lazy_gettext('Please enter a JSON schema'))])
    org_id = SelectField(lazy_gettext('Organization'),
                    [validators.Required(lazy_gettext('Please select an organization'))],
                    coerce=int)
    org_id.choices = [(0, '')]

    submit = SubmitField(lazy_gettext('Save'))


class UserForm(FlaskForm):
    """
    Create or edit a user (for the administrator).
    """
    login = TextField(lazy_gettext('Login'),
            [validators.Length(min=3, max=30),
            validators.Required(lazy_gettext('Please enter your login.'))])
    password = PasswordField(lazy_gettext('Password'))
    public_profile = BooleanField(lazy_gettext('Public profile'), default=True)
    is_active = BooleanField(lazy_gettext('Active'), default=True)
    is_admin = BooleanField(lazy_gettext('Admin'), default=False)
    is_api = BooleanField(lazy_gettext('API'), default=False)
    submit = SubmitField(lazy_gettext('Save'))


class ProfileForm(FlaskForm):
    """
    Edit a profile.
    """
    login = TextField(lazy_gettext('Login'),
            [validators.Length(min=3, max=30),
            validators.Required(lazy_gettext('Please enter your login.'))])
    password = PasswordField(lazy_gettext('Password'))
    public_profile = BooleanField(lazy_gettext('Public profile'), default=True)
    submit = SubmitField(lazy_gettext('Save'))
