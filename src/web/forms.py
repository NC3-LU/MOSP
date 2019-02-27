#! /usr/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlparse
from flask import flash, url_for, redirect, request, current_app
from flask_wtf import FlaskForm
from wtforms import (TextField, TextAreaField, PasswordField, BooleanField,
                     SelectField, SubmitField, validators, HiddenField,
                     SelectMultipleField, HiddenField)
from werkzeug.exceptions import NotFound, HTTPException
from flask_babel import lazy_gettext

from lib import misc_utils
from web.models import User, Organization, License


class RedirectForm(FlaskForm):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        super(RedirectForm, self).__init__(*args, **kwargs)
        if not self.next.data:
            self.next.data = request.args.get('next') or request.referrer
        try:
            ref_url = urlparse(self.next.data)
            if ref_url.path == '/':
                self.next.data = 'user/schemas'
            else:
                # Will raise an exception if no endpoint exists for the url
                current_app.create_url_adapter(request).match(ref_url.path)
        except NotFound:
            print('not found')
            self.next.data = 'user/schemas'
        except HTTPException:
            # Any other exceptions
            pass


    @property
    def redirect_target(self):
        return self.next.data


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
    licenses = SelectMultipleField(lazy_gettext('Licenses'),
                            [validators.Required(lazy_gettext('Please choose a license'))],
                            coerce=int)
    schema_id = HiddenField(lazy_gettext('Validated by'))
    org_id = SelectField(lazy_gettext('Organization'),
                    [validators.Required(lazy_gettext('Please select an organization'))],
                    coerce=int)
    org_id.choices = [(0, '')]

    submit = SubmitField(lazy_gettext('Save'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.licenses.choices = [(license.id, license.name) \
                                        for license in License.query.all()]


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


class OrganizationForm(FlaskForm):
    """
    Create or edit an organization (for the administrator).
    """
    name = TextField(lazy_gettext('Name'),
            [validators.Length(min=3, max=30),
            validators.Required(lazy_gettext('Please enter a name.'))])
    description = TextAreaField(lazy_gettext('Description'),
                    [validators.Required(lazy_gettext('Please enter a description'))])
    organization_type = TextField(lazy_gettext('Type'),
                    [validators.Required(lazy_gettext('Please enter a type'))])
    website = TextField(lazy_gettext('Website'),
                    [validators.Required(lazy_gettext('Please enter a website'))])
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
