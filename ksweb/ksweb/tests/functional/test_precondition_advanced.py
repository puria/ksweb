# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model
from tg import session


class TestPreconditionAdvanced(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.category = self._get_category('Area 1')

    def test_access_new_permission_not_garanted(self):
        self.app.get('/precondition/advanced/new', status=302)

    def test_access_new_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/precondition/advanced/new', params=dict(workspace=self.category._id))
        assert resp_admin.status_code == 200

    def test_access_new_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/precondition/advanced/new', params=dict(workspace=self.category._id))
        assert resp_lawyer.status_code == 200

    def test_post_precondition_advanced(self):
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
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'], qa_params['link'], qa_params['answer_type'], qa_params['answers'])
        qa = self._get_qa_by_title(qa_params['title'])

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

        qa2_params = {
            'title': 'Title of QA2',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA2',
            'link': 'http://www.axant.it',
            'answer_type': 'multi',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa2_params['title'], qa2_params['category'], qa2_params['question'], qa2_params['tooltip'], qa2_params['link'], qa2_params['answer_type'], qa2_params['answers'])
        qa2 = self._get_qa_by_title(qa2_params['title'])

        precondition2_params = {
            'title': 'Have resp2',
            'category': str(category1._id),
            'question': str(qa2._id),
            'answer_type': 'what_response',
            'interested_response': ['Risposta2']
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=precondition2_params
        )

        precond1 = model.Precondition.query.get(title=precondition1_params['title'])
        precond2 = model.Precondition.query.get(title=precondition2_params['title'])

        #  Ora che ho i 2 filtri semplici posso creare il filtro avanzato
        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions': [
                {
                    'type': 'precondition',
                    'content': str(precond1._id)
                },
                {
                    'type': 'operator',
                    'content': 'or'
                },
                {
                    'type': 'precondition',
                    'content': str(precond2._id)
                 }
            ]
        }

        resp = self.app.post_json(
            '/precondition/advanced/post', params=precond_advanced
        )
        assert not resp.json['errors']

        precond_advanced= model.Precondition.query.get(title=precond_advanced['title'])
        assert precond_advanced.type == 'advanced'

    def test_qa_precondition_involved(self):
        self._login_lawyer()
        self.test_post_precondition_advanced()
        precond = self._get_precond_by_title('Resp1 or Resp2')
        resp = self.app.get(
            '/precondition/qa_precondition', params={'id': str(precond._id)}
        ).json
        assert resp
        qa = self._get_qa_by_title('Title of QA')
        qa2 = self._get_qa_by_title('Title of QA2')
        assert str(qa._id) in resp['qas'].keys()
        assert str(qa2._id) in resp['qas'].keys()

    def test_post_advanced_precondition_with_not_valid_id(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')

        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions': [
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
        assert resp.json['errors']


    def test_post_advanced_operator_not_valid(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')

        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions': [
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
        assert resp.json['errors']

    def test_post_advanced_operator_and_condition_not_valid(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')

        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions': [
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
        assert resp.json['errors']

    def test_post_advanced_condition_syntax_error(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        lawyer = self._get_user('lawyer1@ks.axantweb.com')

        self._create_qa('Title1', category1._id, 'Di che sesso sei', 'tooltip', 'link', 'text', '')

        precond_advanced = {
            'title': 'Resp1 or Resp2',
            'category': str(category1._id),
            'conditions': [
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
        assert resp.json['errors']


    def test_update_advanced_filter(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        advanced_filter = self._create_fake_advanced_precondition_red_animal("Title")

        precond_advanced = {
            '_id': str(advanced_filter._id),
            'title': 'new title',
            'category': str(workspace._id),
            'conditions': [
                {
                    'type': 'precondition',
                    'content': str(advanced_filter.condition[0])
                },
                {
                    'type': 'operator',
                    'content': 'and'
                },
                {
                    'type': 'precondition',
                    'content': str(advanced_filter.condition[2])
                 }
            ]
        }

        resp = self.app.put_json('/precondition/advanced/put', params=precond_advanced).json
        assert not resp['errors']

        edited_filter = self._get_precond_by_title('new title')
        assert edited_filter
        assert edited_filter.condition[1] == 'and', edited_filter.condition[1]

    def test_update_advanced_filter_no_id(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        advanced_filter = self._create_fake_advanced_precondition_red_animal("Title")

        precond_advanced = {
            'title': 'new title',
            'category': str(workspace._id),
            'conditions': [
                {
                    'type': 'precondition',
                    'content': str(advanced_filter.condition[0])
                },
                {
                    'type': 'operator',
                    'content': 'and'
                },
                {
                    'type': 'precondition',
                    'content': str(advanced_filter.condition[2])
                 }
            ]
        }

        resp = self.app.put_json('/precondition/advanced/put', params=precond_advanced,
                                 status=412).json
        assert resp['errors']

    def test_update_advanced_filter_syntax_error(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        advanced_filter = self._create_fake_advanced_precondition_red_animal("Title")

        precond_advanced = {
            '_id': str(advanced_filter._id),
            'title': 'new title',
            'category': str(workspace._id),
            'conditions': [
                {
                    'type': 'operator',
                    'content': 'and'
                }
            ]
        }

        resp = self.app.put_json('/precondition/advanced/put', params=precond_advanced,
                                 status=412).json
        assert resp['errors']

    def test_update_advanced_filter_with_related_entity(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        advanced_filter = self._create_fake_advanced_precondition_red_animal("Title")
        self._create_output("Title", workspace._id, advanced_filter._id, "balblaba")

        precond_advanced = {
            '_id': str(advanced_filter._id),
            'title': 'new title',
            'category': str(workspace._id),
            'conditions': [
                {
                    'type': 'precondition',
                    'content': str(advanced_filter.condition[0])
                },
                {
                    'type': 'operator',
                    'content': 'and'
                },
                {
                    'type': 'precondition',
                    'content': str(advanced_filter.condition[2])
                 }
            ]
        }

        response = self.app.put_json('/precondition/advanced/put', params=precond_advanced).json
        assert response['redirect_url']

        self.app.get(response['redirect_url'], params=dict(workspace=str(workspace._id)))
        response = self.app.get('/resolve/original_edit',
                                params=dict(workspace=str(workspace._id)))
        response.follow()

        edited_filter = self._get_precond_by_title('new title')
        assert edited_filter
        assert edited_filter.condition[1] == 'and', edited_filter.condition[1]

    def test_edit_advanced_filter(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        advanced_filter = self._create_fake_advanced_precondition_red_animal("Title")

        response = self.app.get('/precondition/advanced/edit',
                                params=dict(_id=advanced_filter._id, workspace=workspace._id))
        assert str(advanced_filter._id) in response

    def test_edit_advanced_filter_wrong_id(self):
        self._login_lawyer()
        workspace = self._get_category('Area 1')
        response = self.app.get('/precondition/advanced/edit', status=412,
                                params=dict(_id='aaaa1231', workspace=workspace._id)).json

        assert response['errors']
        assert response['errors']['_id'] == 'Filter does not exists'