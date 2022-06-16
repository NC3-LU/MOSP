Installation
============

Prerequisites
-------------

Generally speaking, requirements are the following:

- A GNU/Linux distribution (tested on Debian and Ubuntu);
- Python: version >= 3.8 (preferably use `pyenv <https://github.com/pyenv/pyenv>`_)
  and a dependency manager (for example `Poetry <https://python-poetry.org>`_);
- A PostgreSQL server >= 12.x: persistent storage.


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



Deployment
----------

The service can be deployed via several ways:

.. contents::
    :local:
    :depth: 1


From the source
~~~~~~~~~~~~~~~

Clone the repository and use a Python virtualenv.

.. code-block:: bash

    $ sudo apt install python3-pip python3-venv
    $ curl -sSL https://install.python-poetry.org | python3 -

    $ git clone https://github.com/CASES-LU/MOSP.git
    $ cd MOSP/
    $ npm install
    $ poetry install --no-dev
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


Heroku
~~~~~~

Simply with this button:

.. image:: https://www.herokucdn.com/deploy/button.png
  :target: https://heroku.com/deploy?template=https://github.com/CASES-LU/MOSP
  :alt: Latest release

And voilà !

The default credentials are *admin* for the login and *password* for the password.

Alternatively, Deploy to Heroku manually:

.. code-block:: bash

    $ git clone https://github.com/CASES-LU/MOSP.git
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



Docker
~~~~~~

Deployment with Docker is well suited for development purposes.

Depending on how you installed Docker on your system, you might have to use ``sudo``,
which is discouraged.

From the repository (currently the recommended way with Docker)
```````````````````````````````````````````````````````````````

.. code-block:: bash

    $ git clone https://github.com/CASES-LU/MOSP
    $ docker-compose up -d

Stats Service will be available at:
http://127.0.0.1:5000

A client should be already created, check:

.. code-block:: bash

    $ docker exec -it statsservice_web /bin/bash

    root@3fa0646b50da:/statsservice# poetry shell
    Spawning shell within /root/.cache/pypoetry/virtualenvs/statsservice-B5Jj2TVj-py3.8
    root@3fa0646b50da:/statsservice# . /root/.cache/pypoetry/virtualenvs/statsservice-B5Jj2TVj-py3.8/bin/activate

    (statsservice-B5Jj2TVj-py3.8) root@3fa0646b50da:/statsservice# flask client_list
    UUID: b4c6f28a-1819-49e6-bf06-8691b29afbc5
    Name: user
    Role: 1
    Token: nV3gH6uE2yBcKRjpjBbtUacnVrhpRNiBHgcvtirj5v4wAvlipAHiq5iG-lKu_1wxKD4Ta1q-G7GJFo__voDo5A
    Sharing Enabled: True
    Created at: 2021-03-04 10:23:59.000847


From the Docker Hub
```````````````````

.. code-block:: bash

    $ docker pull caseslu/mosp
    $ docker run --name mosp -d -p 5000:5000 --rm caseslu/mosp

If you have issues with the database hostname resolution, try:

.. code-block:: bash

    $ docker run --name mosp -d -p 5000:5000 --add-host db:127.0.0.1 --rm caseslu/mosp


From the GitHub registry
````````````````````````

.. code-block:: bash

    $ docker pull ghcr.io/cases-lu/mosp:master
    $ docker run --name mosp -d -p 5000:5000 --rm ghcr.io/cases-lu/mosp:master
