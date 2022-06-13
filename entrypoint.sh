#!/bin/sh

if [ "$DEBUG" ]; then
    set -x
fi
set -eu

FLASK_ENV="$ENVIRONMENT"
FLASK_DEBUG="$DEBUG"
FLASK_APP="$APP"
FLASK_RUN_HOST="$HOST"
FLASK_RUN_PORT="$PORT"

export FLASK_ENV FLASK_DEBUG FLASK_APP FLASK_RUN_HOST FLASK_RUN_PORT

export FLASK_APP=runserver.py
export FLASK_ENV=development
export FLASK_RUN_HOST=0.0.0.0
export FLASK_RUN_PORT=5000
export MOSP_CONFIG=docker.py

prepare_db() {
    FLASK_APP=runserver.py flask db_create || true
    FLASK_APP=runserver.py flask db_init
    FLASK_APP=runserver.py flask db upgrade
    FLASK_APP=runserver.py flask import_licenses_from_spdx
    flask create_admin --login admin --email admin@admin.localhost. --password password || true
}

# waiting for DB to come up
for try in 1 2 3 4 5 6; do
    echo >&2 "migration - attempt $try"
    prepare_db && break || true
    sleep 5
    [ "$try" = "6" ] && exit 1
done

gunicorn --chdir /app --workers 2 --bind 0.0.0.0:5000 runserver:application
