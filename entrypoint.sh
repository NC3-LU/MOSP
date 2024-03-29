#!/bin/sh

set -x
set -eu

FLASK_APP="$FLASK_APP"
FLASK_ENV="$ENVIRONMENT"
FLASK_RUN_HOST="$HOST"
FLASK_RUN_PORT="$PORT"

export FLASK_ENV FLASK_APP FLASK_RUN_HOST FLASK_RUN_PORT

prepare_db() {
    flask db_create || true
    flask db_init
    flask db upgrade
    flask import_licenses_from_spdx
    flask create_admin --login admin --email admin@admin.localhost --password password || true
}

# waiting for DB to come up
for try in 1 2 3 4 5 6; do
    echo >&2 "migration - attempt $try"
    prepare_db && break || true
    sleep 5
    [ "$try" = "6" ] && exit 1
done

gunicorn --chdir /app --workers 2 --bind 0.0.0.0:5000 app:application
