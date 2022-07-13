#! /usr/bin/env python
import json
import logging

import click

import mosp.models
import mosp.scripts
from mosp.bootstrap import application
from mosp.bootstrap import db
from mosp.models import Event

logger = logging.getLogger("commands")


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
        mosp.models.db_create(
            db,
            application.config["DB_CONFIG_DICT"],
            application.config["DATABASE_NAME"],
        )


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
@click.option("--login", default="admin", help="Login")
@click.option("--email", default="admin@admin.localhost", help="Email")
@click.option("--password", default="password", help="Password")
def create_user(login, email, password):
    "Initializes a user"
    print(f"Creation of the user {login}…")
    with application.app_context():
        mosp.scripts.create_user(login, email, password, True, False)


@application.cli.command("create_admin")
@click.option("--login", default="admin", help="Login")
@click.option("--email", default="admin@admin.localhost", help="Email")
@click.option("--password", default="password", help="Password")
def create_admin(login, email, password):
    "Initializes an admin user"
    print(f"Creation of the admin user {login}…")
    with application.app_context():
        mosp.scripts.create_user(login, email, password, True, True)


@application.cli.command("clean_events")
def clean_events():
    "Clean events related to Web crawlers."
    print("Cleaning events...")
    count = 0
    crawlers = []
    try:
        with open("./contrib/crawler-user-agents.json") as json_file:
            crawlers = json.load(json_file)
    except Exception:
        print("JSON file with the list of crawler user agents not found.")
    for crawler in crawlers:
        events = Event.query.filter(Event.initiator.op("~")(crawler["pattern"]))
        count += events.count()
        events.delete(synchronize_session=False)
    db.session.commit()
    print(f"Events deleted: {count}")
