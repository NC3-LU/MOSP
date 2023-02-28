Installation
============

Prerequisites
-------------

Generally speaking, requirements are the following:

- A GNU/Linux distribution (tested on Debian and Ubuntu);
- Python: version >= 3.8 (preferably use `pyenv <https://github.com/pyenv/pyenv>`_)
  and a dependency manager (for example `Poetry <https://python-poetry.org>`_);
- A PostgreSQL server >= 12.x: persistent storage.



Deployment
----------

The service can be deployed via several ways:

.. contents::
    :local:
    :depth: 1


From the source
~~~~~~~~~~~~~~~

Creation of a PostgreSQL user:

.. code-block:: bash

    $ sudo apt install postgresql
    $ sudo -u postgres createuser <username>
    $ sudo -u postgres psql
    psql (11.2 (Ubuntu 11.2-1))
    Type "help" for help.
    postgres=# ALTER USER <username> WITH encrypted password '<password>';
    postgres=# ALTER USER <username> WITH SUPERUSER;
    ALTER ROLE
    postgres-# \q

The user name and password chosen must be specified later in the configuration file.
Get the source code and install the software:

.. code-block:: bash

    $ sudo apt install python3-pip python3-venv
    $ curl -sSL https://install.python-poetry.org | python3 -

    $ git clone https://github.com/NC3-LU/MOSP
    $ cd MOSP/
    $ npm install
    $ poetry install --only main
    $ poetry shell
    $ pybabel compile -d mosp/translations
    $ export FLASK_APP=runserver.py
    $ export FLASK_ENV=development
    $ flask db_create
    $ flask db_init
    $ flask import_licenses_from_spdx
    $ flask create_admin --login <login> --password <password>
    $ flask run
     * Serving Flask app "runserver" (lazy loading)
     * Environment: development
     * Debug mode: on
     * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
     * Restarting with stat
     * Debugger is active!
     * Debugger PIN: 221-873-938


For production you should use `Gunicorn <https://gunicorn.org>`_ or ``mod_wsgi``.


Docker
~~~~~~

.. code-block:: bash

    $ git clone https://github.com/NC3-LU/MOSP
    $ cd MOSP/
    $ docker-compose up -d

MOSP will be available at:
http://127.0.0.1:5000

You can connect with the login *admin* and the password *password*.

If you want to connect in the container:

.. code-block:: bash

    $ docker exec -it mosp /bin/bash


Heroku
~~~~~~

Simply with this button:

.. image:: https://www.herokucdn.com/deploy/button.png
  :target: https://heroku.com/deploy?template=https://github.com/NC3-LU/MOSP
  :alt: Latest release

And voilà !

The default credentials are *admin* for the login and *password* for the password.

Alternatively, Deploy to Heroku manually:

.. code-block:: bash

    $ git clone https://github.com/NC3-LU/MOSP
    $ cd MOSP/
    $ heroku create --region eu <name-of-your-instance>
    $ heroku addons:add heroku-postgresql:hobby-dev
    $ heroku config:set HEROKU='1'
    $ heroku buildpacks:add --index 1 heroku/python
    $ heroku buildpacks:add --index 2 https://github.com/heroku/heroku-buildpack-nodejs
    $ git push heroku master
    $ heroku run init
    $ heroku run flask import_licenses_from_spdx
    $ heroku ps:scale web=1


If you want to create other users programmatically:

.. code-block:: bash

    $ heroku run flask create_user --login <nickname> --password <password>
    $ heroku run flask create_admin --login <nickname> --password <password>
