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

        category1 = self._get_category('Categoria 1')
        precondition = self._create_fake_simple_precondition('Precondition 1', category1._id)

        output_params = {
            'title': 'Title of Output',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'content': [
                {
                    'type': "text",
                    'content': "content",
                    'title': ""
                }
            ]
        }

        resp = self.app.post_json(
            '/output/post', params=output_params
        ).json

        output = model.Output.query.get(title=output_params['title'])

        assert output
        assert resp['errors'] is None, resp

    def test_creation_output_with_fake_qa_related(self):
        self._login_lavewr()

        category1 = self._get_category('Categoria 1')
        precondition = self._create_fake_simple_precondition('Precondition 1', category1._id)
        fake_qa = self._create_fake_qa('Fake name')
        output_params = {
            'title': 'Title of Output',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'content': [
                {
                    'type': "text",
                    'content': "content",
                    'title': ""
                },
                {
                    "content": str(fake_qa._id),
                    "type": "qa_response",
                    "title": fake_qa.title
               }
            ]
        }

        resp = self.app.post_json(
            '/output/post', params=output_params,
            status=412
        ).json

        assert resp['errors'] is not None, resp

    def test_put_output(self):
        self.test_creation_output()
        category1 = self._get_category('Categoria 1')
        precondition = self._get_precond_by_title('Precondition 1')

        output1 = self._get_output_by_title('Title of Output')
        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'content': [
                {
                    'type': 'text',
                    'content': "content",
                    'title': ""
                },
                {
                    'type': 'text',
                    'content': "Ciao a tutti",
                    'title': ""
                }
            ]
        }

        resp = self.app.put_json(
            '/output/put', params=output_params
        ).json

        output_updated = self._get_output_by_title('Title of Output edited')
        assert output_updated, output_updated
        assert output_updated._id == output1._id
        assert output_updated.title == output_params['title']
        assert output_updated.content == output_params['content']

    def test_put_output_with_fake_qa_related(self):
        self.test_creation_output()
        category1 = self._get_category('Categoria 1')
        precondition = self._get_precond_by_title('Precondition 1')

        output1 = self._get_output_by_title('Title of Output')
        fake_qa = self._create_fake_qa('Fake name')

        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'content': [
                {
                    'type': 'text',
                    'content': "content",
                    'title': ""
                },
                {
                    "content": str(fake_qa._id),
                    "type": "qa_response",
                    "title": fake_qa.title
               }
            ]
        }

        resp = self.app.put_json(
            '/output/put', params=output_params,
            status=412
        ).json
        assert resp['errors'] is not None, resp

    def test_edit_output(self):
        self._login_lavewr()
        self.test_creation_output()
        out = self._get_output_by_title('Title of Output')
        resp = self.app.get(
            '/output/edit', params={'_id': str(out._id)}
        )
        assert out._id in resp

    def test_creation_output_with_errors(self):
        self._login_lavewr()

        output_params = {
            'title': '1',
            'category': '56c59ab417928003321d5a55',
            'precondition': '56c59ab417928003321d5a55',
            'content': [
                {
                    'type': "text",
                    'content': "content",
                    'title': ""
                }
            ]
        }

        resp = self.app.post_json(
            '/output/post', params=output_params, status=412
        ).json['errors']

        output = model.Output.query.get(title=output_params['title'])

        assert resp['category'] == 'Categoria non esistente', resp
        assert resp['precondition'] == 'Filtro non esistente', resp
        assert resp['title'] == 'Must be at least 2 characters', resp
        assert output is None

    def test_sidebar_output(self):
        self._login_lavewr()

        self._create_fake_output("Out1")
        self._create_fake_output("Out2")
        resp = self.app.get('/output/sidebar_output')
        assert "Out1" in resp
        assert "Out2" in resp

    def test_human_readable_details(self):
        self._login_lavewr()

        out1 = self._create_fake_output("Out1")

        resp = self.app.get('/output/human_readable_details', params={'_id': out1._id})
        assert 'human_readbale_content' in resp
        assert out1._id in resp
