#! /bin/sh

pybabel extract -F src/web/translations/babel.cfg -k lazy_gettext -o src/web/translations/messages.pot src/web/
poedit src/web/translations/fr/LC_MESSAGES/messages.po
