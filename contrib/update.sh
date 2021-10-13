#! /usr/bin/env bash

#
# Update MOSP.
#

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

set -e
#set -x

export FLASK_APP=runserver.py

git pull origin master --tags
npm ci
poetry install --no-dev
poetry run pybabel compile -d mosp/translations
poetry run flask db upgrade

echo -e "✨ 🌟 ✨"
echo -e "${GREEN}MOSP updated. You can now restart the service.${NC} For example:"
echo "    sudo systemctl restart apache2.service"

exit 0
