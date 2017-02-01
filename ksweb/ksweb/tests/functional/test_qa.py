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

        category1 = self._get_category('Categoria 1')
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
        auto_precondition = model.Precondition.query.get(title=qa_text_params['title']+' compilata')

        assert qa_text
        assert resp['errors'] is None
        assert auto_precondition



    def test_post_valid_qa_single_with_not_valid_answers(self):
        self._login_lavewr()

        category1 = self._get_category('Categoria 1')
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
        assert resp['errors']['answers'] == "Please add at least one more answer"

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
        assert resp['errors']['answers'] == "Please add at least one more answer"

    def test_post_valid_qa_single(self):
        self._login_lavewr()

        category1 = self._get_category('Categoria 1')

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
        category1 = self._get_category('Categoria 1')
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

        category1 = self._get_category('Categoria 1')

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

    def test_get_one(self):
        self._login_lavewr()

        category1 = self._get_category('Categoria 1')

        qa_text_multi = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': "multi",
            'answers': ['First', 'Second']
        }

        resp = self.app.post_json(
            '/qa/post', params=qa_text_multi,
        )

        qa = model.Qa.query.get(title=qa_text_multi['title'])

        resp = self.app.get('/qa/get_one', params={'id':str(qa._id)}).json
        assert resp['qa']['title'] == qa_text_multi['title']
        assert str(resp['qa']['_category']) == qa_text_multi['category']
        assert resp['qa']['question'] == qa_text_multi['question']
        assert resp['qa']['tooltip'] == qa_text_multi['tooltip']
        assert resp['qa']['link'] == qa_text_multi['link']
        assert resp['qa']['type'] == qa_text_multi['answer_type'], (resp, qa_text_multi)
        assert resp['qa']['answers'] == qa_text_multi['answers']

        assert resp['qa']['_id'] == str(qa._id), "%s - %s" % (resp['qa']['_id'], qa._id)

    def test_get_single_or_multi_question(self):
        self._login_lavewr()

        self.test_post_valid_qa_text()
        self.test_post_valid_qa_multi()
        self.test_post_valid_qa_single()

        resp = self.app.get('/qa/get_single_or_multi_question').json
        assert len(resp['questions']) == 2
