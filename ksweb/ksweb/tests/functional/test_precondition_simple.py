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

    def test_post_precondition_simple_what_response(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'], qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa(qa_params['title'])

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

        precond_advanced= model.Precondition.query.get(title=precondition_params['title'])

        assert precond_advanced.type == 'simple'
        assert errors == None

    def test_post_precondition_advanced_what_response(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'], qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa(qa_params['title'])

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

        precond_advanced= model.Precondition.query.get(title=precondition_params['title'])

        assert precond_advanced.type == 'advanced'
        assert errors == None

    def test_post_precondition_advanced_have_response(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'], qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa(qa_params['title'])

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

        precond_advanced= model.Precondition.query.get(title=precondition_params['title'])

        assert precond_advanced.type == 'advanced'
        assert errors == None

    def test_post_precondition_advanced_what_response_error(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'], qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa(qa_params['title'])

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

        assert errors is not None

    def test_sidebar_precondition(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        category2 = self._get_category('Category_2')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')
        self._create_precondition('Precond1', lawyer, category1._id)
        self._create_precondition('Precond2', lawyer, category2._id)
        resp = self.app.get('/precondition/sidebar_precondition')

        assert 'Category_1' in resp
        assert 'Category_2' in resp
        assert 'Precond1' in resp
        assert 'Precond2' in resp

    def test_available_preconditions(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')
        self._create_precondition(title='Precond1', user=lawyer, category_id=category1._id, visible=True)
        self._create_precondition(title='Precond2', user=lawyer, category_id=category1._id, visible=False)
        resp = self.app.get('/precondition/available_preconditions')
        assert "Precond1" in resp
        assert "Precond2" not in resp
