# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model


class TestQaController(TestController):
    application_under_test = 'main'

    def test_access_permission_not_garanted(self):
        self.app.get('/qa/get_all', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/qa/get_all')
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lavewr()
        resp_lawyer = self.app.get('/qa/get_all')
        assert resp_lawyer.status_code == 200

    def test_new_qua(self):
        self._login_admin()
        resp_admin = self.app.get('/qa/new')
        assert resp_admin.status_code == 200

    def test_post_valid_qa_text(self):
        self._login_lavewr()

        category1 = self._get_category('Category_1')
        qa_text_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'text',
            'answers': ''
        }

        resp = self.app.post_json(
            '/qa/post', params=qa_text_params
        ).json
        qa_text = model.Qa.query.get(title=qa_text_params['title'])
        assert qa_text
        assert resp['errors'] == None

    def test_post_valid_qa_single_with_not_valid_answers(self):
        self._login_lavewr()

        category1 = self._get_category('Category_1')
        qa_text_single_missing_answers = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers':''
        }

        resp = self.app.post_json(
            '/qa/post', params=qa_text_single_missing_answers, status=412
        ).json
        assert resp['errors']['answers'] == "Inserire almeno due risposte"

        qa_text_single_missing_one_answers = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['First']
        }
        resp = self.app.post_json(
            '/qa/post', params=qa_text_single_missing_one_answers, status=412
        ).json
        assert resp['errors']['answers'] == "Inserire almeno due risposte"

    def test_post_valid_qa_single(self):
        self._login_lavewr()

        category1 = self._get_category('Category_1')

        qa_text_single = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['First', 'Second']
        }
        resp = self.app.post_json(
            '/qa/post', params=qa_text_single,
        ).json

        qa_single = model.Qa.query.get(title=qa_text_single['title'])
        assert qa_single
        assert resp['errors'] == None

    def test_post_valid_qa_multi_with_not_valid_answers(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        qa_text_multi_missing_answers = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'multi',
            'answers': ''
        }

        resp = self.app.post_json(
            '/qa/post', params=qa_text_multi_missing_answers, status=412
        )
        errors = resp.json['errors']
        assert errors['answers'] == "Inserire almeno due risposte"


        qa_text_multi_missing_one_answers = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'multi',
            'answers': ['First']
        }
        resp = self.app.post_json(
            '/qa/post', params=qa_text_multi_missing_one_answers, status=412
        )
        errors = resp.json['errors']

        assert errors['answers'] == "Inserire almeno due risposte"

    def test_post_valid_qa_multi(self):
        self._login_lavewr()

        category1 = self._get_category('Category_1')

        qa_text_multi = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'multi',
            'answers': ['First', 'Second']
        }

        resp = self.app.post_json(
            '/qa/post', params=qa_text_multi,
        )
        errors = resp.json['errors']

        qa_multi = model.Qa.query.get(title=qa_text_multi['title'])
        assert qa_multi
        assert errors == None
