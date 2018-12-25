# -*- coding: utf-8 -*-
from bson import ObjectId
from ksweb.lib.utils import get_entities_from_str
from ksweb.tests import TestController
from ksweb import model
from nose.tools import ok_


class TestOutput(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.workspace = self._get_workspace('Area 1')

    def test_access_permission_not_garanted(self):
        self.app.get('/output/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/output', params=dict(workspace=self.workspace._id))
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/output', params=dict(workspace=self.workspace._id))
        assert resp_lawyer.status_code == 200

    def test_new_precondition_simple(self):
        self._login_admin()
        resp_admin = self.app.get('/output/new', params=dict(workspace=self.workspace._id))
        assert resp_admin.status_code == 200

    def test_creation_error_check_without_precondition(self):
        self._login_lawyer()
        workspace = self._get_workspace('Area 1')
        output_params = {
            'title': 'Title of Output',
            'workspace': str(workspace._id),
            'content': []
        }
        resp = self.app.post_json('/output/post', params=output_params, status=412).json
        output = model.Output.query.get(title=output_params['title'])
        assert not output
        assert resp['errors']

    def test_creation_output(self):
        self._login_lawyer()

        workspace1 = self._get_workspace('Area 1')
        precondition = self._create_fake_simple_precondition('Precondition 1', workspace1._id)

        output_params = {
            'title': 'Title of Output',
            'workspace': str(workspace1._id),
            'precondition': str(precondition._id),
            'html': '<p>Io sono il tuo editor</p>',
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

        workspace1 = self._get_workspace('Area 1')
        precondition = self._create_fake_simple_precondition('Precondition 1', workspace1._id)
        fake_qa = self._create_fake_qa('Fake name')
        output_params = {
            'title': 'Title of Output',
            'workspace': str(workspace1._id),
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
        assert resp['errors']['html'] == 'Enter a value'

    def test_put_output(self):
        self.test_creation_output()
        workspace1 = self._get_workspace('Area 1')
        precondition = self._get_precond_by_title('Precondition 1')

        output1 = self._get_output_by_title('Title of Output')
        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'workspace': str(workspace1._id),
            'precondition': str(precondition._id),
            'html': '<p>Io sono il tuo editor</p>',
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

    def test_output_post_without_filter(self):
        self._login_lawyer()
        workspace = self._get_workspace('Area 1')

        output_params = {
            'title': 'Title of Output',
            'workspace': str(workspace._id),
            'html': '<p>Io sono il tuo editor</p>',
            'content': []
        }

        resp = self.app.post_json(
            '/output/post', params=output_params,
            status=200
        ).json

        assert resp, resp
        assert not resp['errors']

    def test_put_output_with_fake_precondition(self):
        self.test_creation_output()
        workspace1 = self._get_workspace('Area 1')

        output1 = self._get_output_by_title('Title of Output')
        fake_qa = self._create_fake_qa('Fake name')

        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'workspace': str(workspace1._id),
            'precondition': str(workspace1._id), # a wrong id by purpose
            'html': 'Io sono il tuo editor @{%s}' % str(fake_qa._id),
        }

        resp = self.app.put_json(
            '/output/put', params=output_params,
            status=412
        ).json

        assert resp is not None
        assert resp['errors'] is not None, resp
        assert resp['errors']['precondition'] == "Filter does not exists", resp['errors']

    def test_put_output_with_fake_qa_related(self):
        self.test_creation_output()
        workspace1 = self._get_workspace('Area 1')
        precondition = self._get_precond_by_title('Precondition 1')

        output1 = self._get_output_by_title('Title of Output')
        fake_qa = self._create_fake_qa('Fake name')

        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'workspace': str(workspace1._id),
            'precondition': str(precondition._id),
            'html': 'Io sono il tuo editor @{%s}' % str(fake_qa.hash),
        }

        resp = self.app.put_json(
            '/output/put', params=output_params,
            status=412
        ).json

        assert resp is not None
        assert resp['errors'] is not None, resp
        assert resp['errors']['content'] == "The Question/s {'%s'} is not related to the filter" % str(fake_qa._id), resp['errors']['content']

    def test_update_output_with_related_entities(self):
        self._login_lawyer()
        workspace = self._get_workspace('Area 1')
        document = self._create_fake_document("Title", workspace_id=workspace._id)
        outputs, _ = get_entities_from_str(document.html)
        output1 = outputs[0]

        output_params = {
            '_id': str(output1._id),
            'title': 'Title of Output edited',
            'workspace': str(workspace._id),
            'precondition': str(output1.precondition._id),
            'html': '<p>Io sono il tuo editor</p>'
        }

        response = self.app.put_json('/output/put', params=output_params).json
        ok_(response['redirect_url'])
        self.app.get(response['redirect_url'])
        response = self.app.get('/resolve/original_edit',
                                params=dict(workspace=output_params['workspace']))
        response.follow()
        output_edited = model.Output.query.get(_id=ObjectId(output1._id))
        assert output_edited['title'] == output_params['title']


    def test_edit_output(self):
        self._login_lawyer()
        self.test_creation_output()
        out = self._get_output_by_title('Title of Output')
        resp = self.app.get(
            '/output/edit', params={'_id': str(out._id), 'workspace': out._workspace}
        )
        assert str(out._id) in resp

    def test_creation_output_with_errors(self):
        self._login_lawyer()

        output_params = {
            'title': '1',
            'workspace': '56c59ab417928003321d5a55',
            'precondition': '56c59ab417928003321d5a55',
            'html': '<p>Io sono il tuo editor</p>',
            'content': []
        }

        resp = self.app.post_json(
            '/output/post', params=output_params, status=412
        ).json

        output = model.Output.query.get(title=output_params['title'])

        assert resp
        resp = resp['errors']
        assert resp['workspace'] == 'Workspace does not exists', resp
        assert resp['precondition'] == 'Filter does not exists', resp
        assert resp['title'] == 'Must be at least 2 characters', resp
        assert output is None

    def test_human_readable_details(self):
        self._login_lawyer()
        out1 = self._create_fake_output("Out1")
        resp = self.app.get('/output/human_readable_details', params={'_id': out1._id})
        assert 'human_readable_content' in resp
        assert str(out1._id) in resp


class TestOutputPlus(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.workspace = self._get_workspace('Area 1')

    def test_output_plus_creation(self):
        self._login_lawyer()
        self.app.get('/output_plus/post', params=dict(
            highlighted_text='output_plus',
            workspace=str(self.workspace._id),
        ), status=200)

        assert self._get_output_by_title('output_plus')

    def test_output_plus_with_nested_output(self):
        self._login_lawyer()
        nested_output = self._create_fake_output("nested_output")
        self.app.post_json('/output_plus/post', params=dict(
            highlighted_text='output_plus',
            workspace=str(self.workspace._id),
            list_=["#{%s}" % str(nested_output._id)],
        ), status=200)

        assert self._get_output_by_title('output_plus')
