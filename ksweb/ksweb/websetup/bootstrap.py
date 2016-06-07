# -*- coding: utf-8 -*-
"""Setup the ksweb application"""
from __future__ import print_function, unicode_literals
from ksweb import model


def bootstrap(command, conf, vars):
    """Place any commands to setup ksweb here"""

    # <websetup.bootstrap.before.auth
    g = model.Group()
    g.group_name = 'managers'
    g.display_name = 'Managers Group'

    p = model.Permission()
    p.permission_name = 'manage'
    p.description = 'This permission gives an administrative right'
    p.groups = [g]

    u = model.User()
    u.user_name = 'admin'
    u.display_name = 'Example admin'
    u.email_address = 'admin@somedomain.com'
    u.groups = [g]
    u.password = 'adminks'

    g1 = model.Group()
    g1.group_name = 'lawyer'
    g1.display_name = 'Lawyer Group'

    p1 = model.Permission()
    p1.permission_name = 'lawyer'
    p1.description = 'This permission gives an lawyer right'
    p1.groups = [g1]

    u1 = model.User()
    u1.user_name = 'lawyer'
    u1.display_name = 'Lawyer'
    u1.email_address = 'lawyer1@somedomain.com'
    u1.groups = [g1]
    u1.password = 'lawyerks'

    u2 = model.User()
    u2.user_name = 'user'
    u2.display_name = 'Example User'
    u2.email_address = 'user@somedomain.com'
    u2.password = 'userks'

    c1 = model.Category(
        name="Category 1",
        visible=True
    )

    c2 = model.Category(
        name="Category 2",
        visible=True
    )

    c3 = model.Category(
        name="Not Visible Category",
        visible=False
    )

    model.DBSession.flush()
    model.DBSession.clear()

    # <websetup.bootstrap.after.auth>
