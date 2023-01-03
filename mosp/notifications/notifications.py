#! /usr/bin/env python
# MOSP - A platform for creating, editing and sharing JSON objects.
# Copyright (C) 2018-2023 Cédric Bonhomme - https://www.cedricbonhomme.org
# Copyright (C) 2018-2023 Luxembourg House of Cybersecurity
#
# For more information: https://github.com/NC3-LU/MOSP
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import datetime

from flask import render_template

from mosp.bootstrap import application
from mosp.lib.user_utils import generate_confirmation_token
from mosp.notifications import emails


def account_recovery(user):
    """Account recovery."""
    token = generate_confirmation_token(user.login)
    expire_time = datetime.datetime.now() + datetime.timedelta(
        seconds=application.config["TOKEN_VALIDITY_PERIOD"]
    )

    plaintext = render_template(
        "emails/account_recovery.txt",
        user=user,
        instance_url=application.config["INSTANCE_URL"],
        token=token,
        expire_time=expire_time,
    )

    emails.send(
        to=user.email,
        subject="[MOSP] Account recovery",
        plaintext=plaintext,
    )


def new_password_notification(user, password):
    """
    New password notification.
    """
    plaintext = render_template("emails/new_password.txt", user=user, password=password)
    emails.send(
        to=user.email,
        subject="[MOSP] New password",
        plaintext=plaintext,
    )


def confirm_account(user):
    """
    Account creation notification.
    """
    token = generate_confirmation_token(user.login)
    expire_time = datetime.datetime.now() + datetime.timedelta(
        seconds=application.config["TOKEN_VALIDITY_PERIOD"]
    )

    plaintext = render_template(
        "emails/account_activation.txt",
        user=user,
        instance_url=application.config["INSTANCE_URL"],
        token=token,
        expire_time=expire_time,
    )

    emails.send(
        to=user.email,
        subject="[MOSP] Account creation",
        plaintext=plaintext,
    )
