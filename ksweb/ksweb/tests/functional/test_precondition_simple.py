# -*- coding: utf-8 -*-
from ksweb.tests import TestController, load_app, setup_app
from ksweb import model


class TestPreconditionSimple(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.category = self._get_category('Area 1')

    def test_access_permission_not_garanted(self):
        self.app.get('/precondition/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/precondition', params=dict(workspace=self.category._id))
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/precondition',  params=dict(workspace=self.category._id))
        assert resp_lawyer.status_code == 200

    def test_new_precondition_simple(self):
        self._login_admin()
        resp_admin = self.app.get('/precondition/simple/new',  params=dict(workspace=self.category._id))
        assert resp_admin.status_code == 200

    def test_post_precondition_simple_what_response(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'],
                        qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa_by_title(qa_params['title'])

        precondition_params = {
            'title': 'Title of the precondition',
            'category': str(category1._id),
            'question': str(qa._id),
            'answer_type': 'what_response',
            'interested_response': [qa_params['answers'][0]]
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=precondition_params
        )
        errors = resp.json['errors']

        precond_advanced = model.Precondition.query.get(title=precondition_params['title'])

        assert precond_advanced.type == 'simple'
        assert errors == None

    def test_post_precondition_advanced_what_response(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'],
                        qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa_by_title(qa_params['title'])

        precondition_params = {
            'title': 'Title of the precondition',
            'category': str(category1._id),
            'question': str(qa._id),
            'answer_type': 'what_response',
            'interested_response': [qa_params['answers'][0], qa_params['answers'][1]]
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=precondition_params
        )
        errors = resp.json['errors']

        precond_advanced = model.Precondition.query.get(title=precondition_params['title'])

        assert precond_advanced.type == 'advanced'
        assert errors == None

    def test_post_precondition_advanced_have_response(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'],
                        qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa_by_title(qa_params['title'])

        precondition_params = {
            'title': 'Title of the precondition',
            'category': str(category1._id),
            'question': str(qa._id),
            'answer_type': 'have_response',
            'interested_response': []
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=precondition_params
        )
        errors = resp.json['errors']

        precond_advanced = model.Precondition.query.get(title=precondition_params['title'])

        assert precond_advanced.type == 'advanced'
        assert errors == None

    def test_post_precondition_advanced_what_response_error(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'],
                        qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa_by_title(qa_params['title'])

        precondition_params = {
            'title': 'Title of the precondition',
            'category': str(category1._id),
            'question': str(qa._id),
            'answer_type': 'what_response',
            'interested_response': []
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=precondition_params, status=412
        )
        errors = resp.json['errors']
        assert errors


    def test_available_preconditions(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')

        self._create_fake_simple_precondition('Precond1', category1._id)
        self._create_fake_simple_precondition('Precond2', category1._id)

        #  Set precond2 to not visible
        precond2 = self._get_precond_by_title('Precond2')
        precond2.visible = False
        model.DBSession.flush()
        resp = self.app.get('/precondition/available_preconditions', params=dict(workspace=category1._id))
        assert "Precond1" in resp
        assert "Precond2" not in resp

    def test_update_simple_filter(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        precondition = self._create_fake_simple_precondition('Precond1', workspace._id)
        precondition_params = {
            '_id': str(precondition._id),
            'title': 'Title of the precondition',
            'category': str(workspace._id),
            'question': str(precondition.get_qa()._id),
            'answer_type': 'what_response',
            'interested_response': []
        }

        response = self.app.put_json('/precondition/simple/put', params=precondition_params).json
        assert response
        assert self._get_precond_by_title(precondition_params['title'])

    def test_update_simple_filter_with_related_entities(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        precondition = self._create_fake_simple_precondition('Precond1', workspace._id)
        self._create_output("Title", workspace._id, precondition._id, "balblaba", "blablbla")

        precondition_params = {
            '_id': str(precondition._id),
            'title': 'Title of the precondition',
            'category': str(workspace._id),
            'question': str(precondition.get_qa()._id),
            'answer_type': 'what_response',
            'interested_response': []
        }

        response = self.app.put_json('/precondition/simple/put', params=precondition_params).json
        assert response['redirect_url']
        self.app.get(response['redirect_url'])
        self.app.get('/resolve/original_edit', params=dict(workspace=str(workspace._id))).follow()
        assert self._get_precond_by_title(precondition_params['title'])

    def test_edit_simple_filter(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        precondition = self._create_fake_simple_precondition('Precond1', workspace._id)
        response = self.app.get('/precondition/simple/edit',
                                params=dict(_id=precondition._id, workspace=workspace._id))
        assert str(precondition._id) in response

    def test_human_redable_simple_filter(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        precondition = self._create_fake_simple_precondition('Precond1', workspace._id)
        response = self.app.get('/precondition/simple/human_readable_details',
                                params=dict(_id=precondition._id)).json
        assert response['precondition']
        assert response['precondition']['_id'] == str(precondition._id)