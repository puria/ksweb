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
            'title': '1',
            'category': '56c59ab417928003321d5a55',
            'precondition': '56c59ab417928003321d5a55',
            'content': 'c'
        }

        resp = self.app.post_json(
            '/output/post', params=output_params, status=412
        ).json['errors']

        output = model.Output.query.get(title=output_params['title'])
        print "reeeesp"
        print resp

        assert resp['content'] == 'Must be at least 2 characters', resp
        assert resp['category'] == 'Categoria non esistente', resp
        assert resp['precondition'] == 'Precondizione non esistente', resp
        assert resp['title'] == 'Must be at least 2 characters', resp
        assert output is None

    def test_sidebar_output(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')
        self._create_precondition(title='Precond1', user=lawyer, category_id=category1._id, visible=True)
        precond1 = self._get_precond_by_title('Precond1')
        self._create_output("Out1", category1, precond1, "Output content")
        resp = self.app.get('/output/sidebar_output')
        assert "Out1" in resp
