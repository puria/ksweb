# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model


class TestOutput(TestController):
    application_under_test = 'main'

    def test_access_permission_not_garanted(self):
        self.app.get('/output/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/output')
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lavewr()
        resp_lawyer = self.app.get('/output')
        assert resp_lawyer.status_code == 200

    def test_new_precondition_simple(self):
        self._login_admin()
        resp_admin = self.app.get('/output/new')
        assert resp_admin.status_code == 200

    def test_creation_output(self):
        self._login_lavewr()

        category1 = self._get_category('Category_1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')
        precondition = self._create_precondition('Precondition 1', lawyer, category1._id)

        output_params = {
            'title': 'Title of Output',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'content': 'content'
        }

        resp = self.app.post_json(
            '/output/post', params=output_params
        ).json

        output = model.Output.query.get(title=output_params['title'])

        assert output
        assert resp['errors'] is None, resp

    def test_creation_output_with_errors(self):
        self._login_lavewr()

        output_params = {
            'title': '123',
            'category': '56c59ab417928003321d5a55',
            'precondition': '56c59ab417928003321d5a55',
            'content': 'cot'
        }

        resp = self.app.post_json(
            '/output/post', params=output_params, status=412
        ).json['errors']

        output = model.Output.query.get(title=output_params['title'])

        assert resp['content'] == 'Must be at least 4 characters', resp
        assert resp['category'] == 'Categoria non esistente', resp
        assert resp['precondition'] == 'Precondizione non esistente', resp
        assert resp['title'] == 'Must be at least 4 characters', resp
        assert output is None