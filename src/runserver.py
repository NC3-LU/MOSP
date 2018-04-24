#! /usr/bin/env python
# -*- coding: utf-8 -*-

from bootstrap import application, populate_g

with application.app_context():
    populate_g()

    from web import views
    application.register_blueprint(views.admin_bp)



if __name__ == '__main__':
    application.run(host=application.config['HOST'],
                    port=application.config['PORT'])
