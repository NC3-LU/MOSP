#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging

import click

import mosp.scripts
import mosp.models
from mosp.bootstrap import application, db

logger = logging.getLogger('commands')


@application.cli.command("uml_graph")
def uml_graph():
    "UML graph from the models."
    with application.app_context():
        mosp.models.uml_graph(db)


@application.cli.command("db_empty")
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        mosp.models.db_empty(db)


@application.cli.command("db_create")
def db_create():
    "Will create the database."
    with application.app_context():
        mosp.models.db_create(db, application.config['DB_CONFIG_DICT'],
                        application.config['DATABASE_NAME'])


@application.cli.command("db_init")
def db_init():
    "Will create the database from conf parameters."
    with application.app_context():
        mosp.models.db_init(db)


@application.cli.command("import_licenses_from_spdx")
def import_licenses_from_spdx():
    "Import licenses from spdx.org."
    print("Importing licenses from spdx.org...")
    with application.app_context():
        mosp.scripts.import_licenses_from_spdx()


@application.cli.command("create_user")
@click.option('--login', default='admin', help='Login')
@click.option('--password', default='password', help='Password')
def create_user(login, password):
    "Initializes a user"
    print("Creation of the user {} ...".format(login))
    with application.app_context():
        mosp.scripts.create_user(login, password, False)


@application.cli.command("create_admin")
@click.option('--login', default='admin', help='Login')
@click.option('--password', default='password', help='Password')
def create_admin(login, password):
    "Initializes an admin user"
    print("Creation of the admin user {} ...".format(login))
    with application.app_context():
        mosp.scripts.create_user(login, password, True)
