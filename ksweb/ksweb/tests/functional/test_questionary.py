# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model


class TestQuestionaryController(TestController):

    application_under_test = 'main'

    def test_access_permission_not_garanted(self):
        self.app.get('/questionary', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/questionary')
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lavewr()
        resp_lawyer = self.app.get('/questionary')
        assert resp_lawyer.status_code == 200

    def test_questionary_create(self):
        self._login_lavewr()
        doc = self._create_fake_document('Fake1')
        resp = self.app.post_json('/questionary/create', params={
            'questionary_title': 'TestQuestionary',
            'document_id': str(doc._id)
        })
        assert resp
