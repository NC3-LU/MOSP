#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, populate_g

with application.app_context():
    populate_g()

    from web import views


if __name__ == '__main__':
    application.run(host=application.config['HOST'],
                    port=application.config['PORT'])
