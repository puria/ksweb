# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model


class TestPreconditionSimple(TestController):
    application_under_test = 'main'

    def test_access_permission_not_garanted(self):
        self.app.get('/precondition/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/precondition')
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lavewr()
        resp_lawyer = self.app.get('/precondition')
        assert resp_lawyer.status_code == 200

    def test_new_precondition_simple(self):
        self._login_admin()
        resp_admin = self.app.get('/precondition/simple/new')
        assert resp_admin.status_code == 200
