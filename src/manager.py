#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from bootstrap import application, db
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

import web.models


logger = logging.getLogger('manager')

Migrate(application, db)
manager = Manager(application)
manager.add_command('db', MigrateCommand)


@manager.command
def uml_graph():
    "UML graph from the models."
    with application.app_context():
        web.models.uml_graph(db)


@manager.command
def db_empty():
    "Will drop every datas stocked in db."
    with application.app_context():
        web.models.db_empty(db)


@manager.command
def db_create():
    "Will create the database."
    with application.app_context():
        web.models.db_create(db, application.config['DB_CONFIG_DICT'],
                             application.config['DATABASE_NAME'])


@manager.command
def db_init():
    "Will create the database from conf parameters."
    with application.app_context():
        web.models.db_init(db)



if __name__ == '__main__':
    manager.run()
