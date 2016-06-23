# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model


class TestPreconditionAdvanced(TestController):
    application_under_test = 'main'

    def test_access_new_permission_not_garanted(self):
        self.app.get('/precondition/advanced/new', status=302)

    def test_access_new_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/precondition/advanced/new')
        assert resp_admin.status_code == 200

    def test_access_new_permission_lawyer(self):
        self._login_lavewr()
        resp_lawyer = self.app.get('/precondition/advanced/new')
        assert resp_lawyer.status_code == 200

    def test_post_precondition_advanced(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        #  Devo creare almeno 1 qa con delle risposte

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

        precondition1_params = {
            'title': 'Have resp1',
            'category': str(category1._id),
            'question': str(qa._id),
            'answer_type': 'what_response',
            'interested_response': ['Risposta1']
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=precondition1_params
        )
        precondition2_params = {
            'title': 'Have resp2',
            'category': str(category1._id),
            'question': str(qa._id),
            'answer_type': 'what_response',
            'interested_response': ['Risposta2']
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=precondition2_params
        )

        precond1 = model.Precondition.query.get(title=precondition1_params['title'])
        precond2 = model.Precondition.query.get(title=precondition2_params['title'])

        #  Ora che ho le due precondizioni posso creare quella composta
        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions':[
                {
                    'type':'precondition',
                    'content':str(precond1._id)
                },
                {
                    'type':'operator',
                    'content':'or'
                },
                {
                    'type':'precondition',
                    'content':str(precond2._id)
                 }
            ]
        }

        resp = self.app.post_json(
            '/precondition/advanced/post', params=precond_advanced
        )
        errors = resp.json['errors']
        precond_advanced= model.Precondition.query.get(title=precond_advanced['title'])

        assert precond_advanced.type == 'advanced'
        assert errors == None

    def test_post_advanced_precondition_with_not_valid_id(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')
        self._create_precondition('Titolo2', lawyer, category1._id)

        #  Ora che ho le due precondizioni posso creare quella composta
        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions':[
                {
                    'type': 'precondition',
                    'content': str(lawyer._id)
                },
                {
                    'type': 'operator',
                    'content': 'or'
                },
                {
                    'type': 'precondition',
                    'content': str(lawyer._id)
                 }
            ]
        }

        resp = self.app.post_json(
            '/precondition/advanced/post', params=precond_advanced, status=412
        )
        errors = resp.json['errors']

        assert errors is not None

    def test_post_advanced_operator_not_valid(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')
        self._create_precondition('Titolo2', lawyer, category1._id)

        #  Ora che ho le due precondizioni posso creare quella composta
        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions':[
                {
                    'type': 'operator',
                    'content': 'fake_operator'
                },
                {
                    'type': 'precondition',
                    'content': str(lawyer._id)
                 }
            ]
        }

        resp = self.app.post_json(
            '/precondition/advanced/post', params=precond_advanced, status=412
        )
        errors = resp.json['errors']

        assert errors is not None

    def test_post_advanced_operator_and_condition_not_valid(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')
        self._create_precondition('Titolo2', lawyer, category1._id)

        #  Ora che ho le due precondizioni posso creare quella composta
        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions':[
                {
                    'type': 'fake_content',
                    'content': 'fake_operator'
                },
                {
                    'type': 'precondition',
                    'content': str(lawyer._id)
                 }
            ]
        }

        resp = self.app.post_json(
            '/precondition/advanced/post', params=precond_advanced, status=412
        )
        errors = resp.json['errors']

        assert errors is not None

    def test_post_advanced_condition_syntax_error(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')
        self._create_precondition('Titolo2', lawyer, category1._id)

        #  Ora che ho le due precondizioni posso creare quella composta
        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions':[
                {
                    'type': 'operator',
                    'content': 'or'
                },
                {
                    'type': 'operator',
                    'content': 'not'
                 }
            ]
        }

        resp = self.app.post_json(
            '/precondition/advanced/post', params=precond_advanced, status=412
        )
        errors = resp.json['errors']

        assert errors is not None
