#! /usr/bin/env python
# -*- coding: utf-8 -*-

# MOSP - A platform for creating, editing and sharing JSON objects.
# Copyright (C) 2018-2021 Cédric Bonhomme - https://www.cedricbonhomme.org
# Copyright (C) 2018-2021 SMILE gie - securitymadein.lu
#
# For more information: https://github.com/CASES-LU/MOSP
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

import logging
import smtplib
from email.mime.nonmultipart import MIMENonMultipart
from email import charset

from mosp.bootstrap import application

# from mosp.decorators import async_maker

logger = logging.getLogger(__name__)


# @async_maker
# def send_async_email(mfrom, mto, msg):
#     try:
#         s = smtplib.SMTP(application.config["NOTIFICATION_HOST"])
#         s.login(
#             application.config["NOTIFICATION_USERNAME"],
#             application.config["NOTIFICATION_PASSWORD"],
#         )
#     except Exception:
#         logger.exception("send_async_email raised:")
#     else:
#         s.sendmail(mfrom, mto, msg.as_bytes().decode(encoding="UTF-8"))
#         s.quit()


def send(*args, **kwargs):
    """
    This functions enables to send email via different method.
    """
    send_smtp(**kwargs)


def send_smtp(to="", subject="", plaintext="", html=""):
    """
    Send an email.
    """
    # Create message container
    msg = MIMENonMultipart("text", "plain", charset="utf-8")
    # Construct a new charset which uses Quoted Printables (base64 is default)
    cs = charset.Charset("utf-8")
    cs.body_encoding = charset.QP
    msg["Subject"] = subject
    msg["From"] = application.config["MAIL_DEFAULT_SENDER"]
    msg["To"] = to

    msg.set_payload(plaintext, charset=cs)

    try:
        s = smtplib.SMTP(application.config["MAIL_SERVER"])
        if application.config["MAIL_USERNAME"] is not None:
            s.login(
                application.config["MAIL_USERNAME"],
                application.config["MAIL_PASSWORD"],
            )
    except ConnectionRefusedError:
        print("Problem when sending email.")
    except Exception:
        logger.exception("send_smtp raised:")
    else:
        try:
            s.sendmail(
                application.config["MAIL_DEFAULT_SENDER"],
                msg["To"],
                msg.as_bytes().decode(encoding="UTF-8"),
            )
            s.quit()
        except Exception:
            pass
