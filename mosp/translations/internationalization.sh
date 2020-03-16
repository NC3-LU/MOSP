#! /bin/sh

pybabel extract -F mosp/translations/babel.cfg -k lazy_gettext -o mosp/translations/messages.pot mosp/
poedit mosp/translations/fr/LC_MESSAGES/messages.po
