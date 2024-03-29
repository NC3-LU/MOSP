#! /usr/bin/env python
from urllib.parse import urlparse

from flask import current_app
from flask import request
from flask_babel import lazy_gettext
from flask_wtf import FlaskForm
from werkzeug.exceptions import HTTPException
from werkzeug.exceptions import NotFound
from wtforms import BooleanField
from wtforms import HiddenField
from wtforms import PasswordField
from wtforms import SelectField
from wtforms import SelectMultipleField
from wtforms import StringField
from wtforms import SubmitField
from wtforms import TextAreaField
from wtforms import validators
from wtforms.fields import EmailField
from wtforms.validators import Email
from wtforms.validators import InputRequired

from mosp.models import JsonObject
from mosp.models import License
from mosp.models import Organization
from mosp.models import User


class RedirectForm(FlaskForm):
    """Redirect form used for the redirection after the sign in."""

    next = HiddenField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.next.data:
            # self.next.data = request.args.get("next") or request.referrer
            self.next.data = request.args.get("next") or "user/schemas"
        try:
            ref_url = urlparse(self.next.data)
            if ref_url.path == "/":
                self.next.data = "user/schemas"
            else:
                # Will raise an exception if no endpoint exists for the url
                adapter = current_app.create_url_adapter(request)
                adapter.match(ref_url.path)  # type: ignore
        except NotFound:
            self.next.data = "user/schemas"
        except HTTPException:
            # Any other exceptions
            pass

    @property
    def redirect_target(self):
        return self.next.data


class SigninForm(RedirectForm):
    """Sign in form."""

    login = StringField(
        lazy_gettext("Login"),
        [
            validators.Length(min=3, max=50),
            validators.InputRequired(lazy_gettext("Please enter your login.")),
        ],
    )
    password = PasswordField(
        lazy_gettext("Password"),
        [
            validators.InputRequired(lazy_gettext("Please enter your password.")),
            validators.Length(min=6, max=500),
        ],
    )
    submit = SubmitField(lazy_gettext("Log In"))

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
            self.login.errors.append(lazy_gettext("Impossible to login."))
        return validated


class SignupForm(FlaskForm):
    """
    Sign up form (registration to MOSP).
    """

    login = StringField(
        lazy_gettext("Login"),
        [validators.InputRequired(lazy_gettext("Please enter your login."))],
    )
    email = EmailField(
        lazy_gettext("Email"),
        [
            validators.Length(min=6, max=256),
            validators.InputRequired(lazy_gettext("Please enter your email address.")),
        ],
    )
    submit = SubmitField(lazy_gettext("Sign up"))

    def validate(self):
        validated = super().validate()
        if User.query.filter(User.login == self.login.data).count():
            self.login.errors.append(lazy_gettext("Login already taken"))
            validated = False
        if self.login.data != User.make_valid_login(self.login.data):
            self.login.errors.append(
                lazy_gettext(
                    "This login has invalid characters. "
                    "Please use letters, numbers, hyphens and underscores only."
                )
            )
            validated = False
        return validated


class AccountRecoveryForm(RedirectForm):
    """Sign in form."""

    login = StringField(
        lazy_gettext("Login"),
        [
            validators.Length(min=3, max=30),
            validators.InputRequired(lazy_gettext("Please enter your login.")),
        ],
    )
    submit = SubmitField(lazy_gettext("OK"))


class AccountConfirmationForm(RedirectForm):
    """Account confirmation and recovery form."""

    password1 = PasswordField(
        lazy_gettext("Password"),
        [
            validators.InputRequired(lazy_gettext("Please enter your password.")),
            validators.Length(min=20, max=500),
            validators.InputRequired(),
            validators.EqualTo(
                "password2", message=lazy_gettext("Passwords must match.")
            ),
        ],
    )
    password2 = PasswordField(
        lazy_gettext("Password"),
        [
            validators.InputRequired(lazy_gettext("Please confirm your password.")),
            validators.Length(min=20, max=500),
        ],
    )
    submit = SubmitField(lazy_gettext("OK"))


class AddObjectForm(FlaskForm):
    """Form to create and edit JsonObject."""

    name = StringField(
        "Name", [validators.InputRequired(lazy_gettext("Please enter a name"))]
    )
    description = TextAreaField(
        lazy_gettext("Description"),
        [validators.InputRequired(lazy_gettext("Please enter a description"))],
    )
    licenses = SelectMultipleField(
        lazy_gettext("Licenses"),
        [validators.InputRequired(lazy_gettext("Please choose a license"))],
        coerce=int,
    )
    refers_to = SelectMultipleField(lazy_gettext("Refers to the objects"), coerce=int)
    referred_to_by = SelectMultipleField(
        lazy_gettext("Referred to by the objects"), coerce=int
    )
    schema_id = HiddenField(lazy_gettext("Validated by"))
    org_id = SelectField(
        lazy_gettext("Organization"),
        [validators.InputRequired(lazy_gettext("Please select an organization"))],
        coerce=int,
    )
    org_id.choices = [(0, "")]

    submit = SubmitField(lazy_gettext("Save"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.licenses.choices = [
            (license.id, license.name) for license in License.query.all()
        ]
        self.refers_to.choices = [
            (jsonobject.id, jsonobject.name) for jsonobject in JsonObject.query.all()
        ]
        self.referred_to_by.choices = [
            (jsonobject.id, jsonobject.name) for jsonobject in JsonObject.query.all()
        ]


class SchemaForm(FlaskForm):
    name = StringField(
        "Name", [validators.InputRequired(lazy_gettext("Please enter a name"))]
    )
    description = TextAreaField(
        lazy_gettext("Description"),
        [validators.InputRequired(lazy_gettext("Please enter a description"))],
    )
    json_schema = TextAreaField(
        "JSON schema",
        [validators.InputRequired(lazy_gettext("Please enter a JSON schema"))],
    )
    org_id = SelectField(
        lazy_gettext("Organization"),
        [validators.InputRequired(lazy_gettext("Please select an organization"))],
        coerce=int,
        default=0,
    )
    org_id.choices = [(0, "")]

    submit = SubmitField(lazy_gettext("Save"))


class UserForm(FlaskForm):
    """Create or edit a user (for the administrator)."""

    login = StringField(
        lazy_gettext("Login"),
        [
            validators.Length(min=3, max=30),
            validators.InputRequired(lazy_gettext("Please enter your login.")),
        ],
    )
    password = PasswordField(lazy_gettext("Password"))
    email = EmailField(
        "Email",
        [
            InputRequired("Please enter your email address."),
            Email("Please enter your email address."),
        ],
    )
    is_active = BooleanField(lazy_gettext("Active"), default=True)
    is_admin = BooleanField(lazy_gettext("Admin"), default=False)
    is_api = BooleanField(lazy_gettext("API"), default=False)
    organizations = SelectMultipleField(lazy_gettext("Organizations"), coerce=int)
    submit = SubmitField(lazy_gettext("Save"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.organizations.choices = [
            (organization.id, organization.name)
            for organization in Organization.query.all()
        ]


class OrganizationForm(FlaskForm):
    """Create or edit an organization (for the administrator)."""

    name = StringField(
        lazy_gettext("Name"),
        [
            validators.Length(min=3, max=30),
            validators.InputRequired(lazy_gettext("Please enter a name.")),
        ],
    )
    description = TextAreaField(
        lazy_gettext("Description"),
        [validators.InputRequired(lazy_gettext("Please enter a description"))],
    )
    organization_type = StringField(lazy_gettext("Type"))
    is_membership_restricted = BooleanField(
        lazy_gettext("Restricted membership"),
        default=True,
        description=lazy_gettext(
            "The membership model of the organization (restricted or not restricted)."
        ),
    )
    website = StringField(lazy_gettext("Website"))
    users = SelectMultipleField(
        lazy_gettext("Members"),
        coerce=int,
        description=lazy_gettext("The members part of the organization."),
    )
    submit = SubmitField(lazy_gettext("Save"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.users.choices = [(user.id, user.login) for user in User.query.all()]


class ProfileForm(FlaskForm):
    """Edit a profile."""

    login = StringField(
        lazy_gettext("Login"),
        [
            validators.Length(min=3, max=30),
            validators.InputRequired(lazy_gettext("Please enter your login.")),
        ],
    )
    password = PasswordField(
        lazy_gettext("Password"),
        [
            validators.InputRequired(lazy_gettext("Please enter your password.")),
            validators.Length(min=20, max=500),
        ],
    )
    email = EmailField(
        "Email",
        [
            InputRequired(lazy_gettext("Please enter your email address.")),
            Email(lazy_gettext("Please enter your email address.")),
        ],
    )
    submit = SubmitField(lazy_gettext("Save"))


class CollectionForm(FlaskForm):
    """Create or edit a collection."""

    name = StringField(
        lazy_gettext("Name"),
        [
            validators.Length(min=3, max=100),
            validators.InputRequired(lazy_gettext("Please enter a name.")),
        ],
    )
    description = TextAreaField(
        lazy_gettext("Description"),
        [validators.InputRequired(lazy_gettext("Please enter a description"))],
    )
    submit = SubmitField(lazy_gettext("Save"))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
