# -*- coding: utf-8 -*-
from bson import ObjectId
from ksweb.tests import TestController
from ksweb import model


class TestOutput(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.category = self._get_category('Area 1')

    def test_access_permission_not_garanted(self):
        self.app.get('/output/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/output', params=dict(workspace=self.category._id))
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/output', params=dict(workspace=self.category._id))
        assert resp_lawyer.status_code == 200

    def test_new_precondition_simple(self):
        self._login_admin()
        resp_admin = self.app.get('/output/new', params=dict(workspace=self.category._id))
        assert resp_admin.status_code == 200

    def test_creation_output(self):
        self._login_lawyer()

        category1 = self._get_category('Area 1')
        precondition = self._create_fake_simple_precondition('Precondition 1', category1._id)

        output_params = {
            'title': 'Title of Output',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'ks_editor': '<p>Io sono il tuo editor</p>',
            'content': []
        }

        resp = self.app.post_json(
            '/output/post', params=output_params
        ).json

        output = model.Output.query.get(title=output_params['title'])

        assert output
        assert resp['errors'] is None, resp

    def test_creation_output_with_fake_qa_related(self):
        self._login_lawyer()

        category1 = self._get_category('Area 1')
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

        assert resp, resp
        assert resp['errors'], resp
        assert resp['errors']['content'] == 'Invalid Filter.'

    def test_put_output(self):
        self.test_creation_output()
        category1 = self._get_category('Area 1')
        precondition = self._get_precond_by_title('Precondition 1')

        output1 = self._get_output_by_title('Title of Output')
        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'ks_editor': '<p>Io sono il tuo editor</p>',
            'content': []
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
        category1 = self._get_category('Area 1')
        precondition = self._get_precond_by_title('Precondition 1')

        output1 = self._get_output_by_title('Title of Output')
        fake_qa = self._create_fake_qa('Fake name')

        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'category': str(category1._id),
            'precondition': str(precondition._id),
            'ks_editor': '<p>Io sono il tuo editor</p>',
            'content': [
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
        assert resp is not None
        assert resp['errors'] is not None, resp
        assert resp['errors']['content'] == 'The question Fake name is not related to the filter', resp['errors']['content']

    def test_update_output_with_related_entities(self):
        self._login_lawyer()
        category = self._get_category('Area 1')
        document = self._create_fake_document("Title", category_id=category._id)
        output_id = document['content'][0]['content']
        output1 = model.Output.query.get(_id=ObjectId(output_id))

        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'category': str(category._id),
            'precondition': str(output1.precondition._id),
            'ks_editor': '<p>Io sono il tuo editor</p>',
            'content': []
        }

        response = self.app.put_json('/output/put', params=output_params).json
        assert response['redirect_url']
        self.app.get(response['redirect_url'])
        response = self.app.get('/resolve/original_edit',
                                params=dict(workspace=output_params['category']))
        response.follow()
        output_edited = model.Output.query.get(_id=ObjectId(output_id))
        assert output_edited['title'] == output_params['title']


    def test_edit_output(self):
        self._login_lawyer()
        self.test_creation_output()
        out = self._get_output_by_title('Title of Output')
        resp = self.app.get(
            '/output/edit', params={'_id': str(out._id), 'workspace': out._category}
        )
        assert out._id in resp

    def test_creation_output_with_errors(self):
        self._login_lawyer()

        output_params = {
            'title': '1',
            'category': '56c59ab417928003321d5a55',
            'precondition': '56c59ab417928003321d5a55',
            'ks_editor': '<p>Io sono il tuo editor</p>',
            'content': []
        }

        resp = self.app.post_json(
            '/output/post', params=output_params, status=412
        ).json

        output = model.Output.query.get(title=output_params['title'])

        assert resp
        resp = resp['errors']
        assert resp['category'] == 'Work Area does not exists', resp
        assert resp['precondition'] == 'Filter does not exists', resp
        assert resp['title'] == 'Must be at least 2 characters', resp
        assert output is None

    # def test_sidebar_output(self):
    #     self._login_lawyer()
    #     category1 = self._get_category('Area 1')
    #     self._create_fake_output("Out1", category1._id)
    #     self._create_fake_output("Out2", category1._id)
    #     resp = self.app.get('/output/sidebar_output', params={'workspace': category1._id})
    #     assert "Out1" in resp
    #     assert "Out2" in resp

    def test_human_readable_details(self):
        self._login_lawyer()
        out1 = self._create_fake_output("Out1")
        resp = self.app.get('/output/human_readable_details', params={'_id': out1._id})
        assert 'human_readbale_content' in resp
        assert out1._id in resp

class TestOutputPlus(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.category = self._get_category('Area 1')

    def test_output_plus_creation(self):
        self._login_lawyer()
        self.app.get('/output_plus/post', params=dict(
            highlighted_text='output_plus',
            workspace=str(self.category._id),
        ), status=200)

        assert self._get_output_by_title('Output output_plus')

    def test_output_plus_with_nested_output(self):
        self._login_lawyer()
        nested_output = self._create_fake_output("nested_output")
        self.app.post_json('/output_plus/post', params=dict(
            highlighted_text='output_plus',
            workspace=str(self.category._id),
            list_=["output_%s" % str(nested_output._id)],
        ), status=200)

        assert self._get_output_by_title('Output output_plus')
