# -*- coding: utf-8 -*-
from __future__ import print_function

import zipfile
import pytz
import io
from datetime import datetime
try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO

from ksweb.tests import TestController


class TestQuestionaryController(TestController):

    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.workspace = self._get_workspace('Area 1')

    def test_access_permission_not_garanted(self):
        self.app.get('/questionary', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/questionary', params=dict(workspace=self.workspace._id))
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/questionary', params=dict(workspace=self.workspace._id))
        assert resp_lawyer.status_code == 200

    def test_questionary_create(self):
        self._login_lawyer()
        doc = self._create_fake_document('Fake1')
        resp = self.app.post_json('/questionary/create', params={
            'questionary_title': 'TestQuestionary',
            'document_id': str(doc._id),
            'workspace':  str(self.workspace._id)
        })
        assert resp

    def test_questionary_create_with_share(self):
        self._login_lawyer()
        email_to_share = 'test@example.com'
        document = self._create_fake_document('Fake1')
        self.app.post_json('/questionary/create', params={
            'questionary_title': 'TestQuestionary',
            'document_id': str(document._id),
            'workspace':  str(self.workspace._id),
            'email_to_share': email_to_share
        })

        user = self._get_user(email_to_share)
        assert user

    def test_compile_questionary(self):
        self._login_lawyer()
        questionary = self._create_fake_questionary('FakeQuestionary', workspace_id=self.workspace._id)
        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id),
            'workspace': self.workspace._id
        }).json
        assert resp['quest_compiled'] is not None, resp
        assert resp['quest_compiled']['completed'] is False, resp

    def test_responde_questionary(self):

        self._login_lawyer()
        questionary = self._create_fake_questionary('FakeQuestionary', workspace_id=self.workspace._id)

        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id),
            'workspace': self.workspace._id
        }).json

        assert resp['quest_compiled']['completed'] is False, resp

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': self.FAKE_RESPONSE[0]
        }).json

        assert resp['quest_compiled']['completed'] is True, resp

    def test_hack_response(self):
        self._login_lawyer()
        questionary = self._create_fake_questionary('FakeQuestionary', workspace_id=self.workspace._id)
        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id),
            'workspace': self.workspace._id
        }).json
        assert resp['quest_compiled']['completed'] is False, resp

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': "Fake response"
        }, status=412).json


    def test_compile_advanced_questionary(self):
        self._login_lawyer()
        workspace1 = self._get_workspace('Area 1')
        fake_advanced_precond = self._create_fake_advanced_precondition_red_animal("Advanced_precond")
        qa_color = self._get_qa_by_title('Favourite color')
        out_1 = self._create_output("example1",
                                    workspace1._id,
                                    fake_advanced_precond._id,
                                    'some html @{%s}' % qa_color.hash)

        qa_animal = self._get_qa_by_title('Favourite color')
        out_2 = self._create_output("example1", workspace1._id,
                                    fake_advanced_precond._id, 'some html  @{%s}' % qa_animal.hash)

        html = '#{%s} #{%s}' % (out_1.hash, out_2.hash)

        document = self._create_document("Advanced_document", workspace1._id, html)
        questionary = self._create_questionary("Advanced_Questionary", document._id)

        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id),
            'workspace': document._workspace
        }).json
        assert resp['quest_compiled']['completed'] is False, resp

        qa_response = {
            'Favourite color': {
                'response': 'Red',
                'status': 200
            },
            'Animal liked': {
                'response': ['Dog', 'Turtle'],
                'status': 200
            }
        }
        rel_qa = self._get_qa(resp['quest_compiled']['qa'])

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': qa_response[rel_qa.title]['response']
        }, status=qa_response[rel_qa.title]['status']).json

        assert resp['quest_compiled']['completed'] is True


    def test_compile_advanced_questionary_not_showing_two_time_same_answer(self):
        self._login_lawyer()
        workspace1 = self._get_workspace('Area 1')
        fake_advanced_precond = self._create_fake_advanced_precondition_red_animal("Advanced_precond")
        qa_color = self._get_qa_by_title('Favourite color')
        out_1 = self._create_output("example1", workspace1._id,
                                    fake_advanced_precond._id, '@{%s}' % str(qa_color.hash))

        qa_animal = self._get_qa_by_title('Favourite color')
        out_2 = self._create_output("example1", workspace1._id,
                                    fake_advanced_precond._id, '@{%s}' % str(qa_animal.hash))
        html = '#{%s} #{%s} #{%s}' % (str(out_1.hash), str(out_2.hash), str(out_1.hash))
        document = self._create_document("Advanced_document", workspace1._id, html)
        questionary = self._create_questionary("Advanced_Questionary", document._id)

        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id),
            'workspace': document._workspace

        }).json
        assert resp['quest_compiled']['completed'] is False, resp

        qa_response = {
            'Favourite color': {
                'response': 'Red',
                'status': 200
            },
            'Animal liked': {
                'response': ['Pig', 'Dog'],
                'status': 200
            }
        }
        rel_qa = self._get_qa(resp['quest_compiled']['qa'])

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': qa_response[rel_qa.title]['response']
        }, status=qa_response[rel_qa.title]['status']).json

        assert resp['quest_compiled']['completed'] is True, resp

    def test_download(self):
        self.test_compile_advanced_questionary()	
        form = self._get_questionary_by_title('Advanced_Questionary')	
        response = self.app.get('/questionary/download', params=dict(_id=str(form._id)))	
	
        assert response
        assert str(form._id) in response.content_disposition	


    def test_completed(self):
        self.test_questionary_create()
        form = self._get_questionary_by_title('TestQuestionary')
        response = self.app.get('/questionary/completed',
                                params=dict(_id=str(form._id), workspace=self.workspace._id),
                                status=200)
        assert response, response

    def test_previous_question(self):
        self.test_questionary_create()
        form = self._get_questionary_by_title('TestQuestionary')
        response = self.app.get('/questionary/previous_question', params=dict(_id=str(form._id)))
        assert response

    def test_creation_date(self):
        self.test_questionary_create()
        form = self._get_questionary_by_title('TestQuestionary')
        utcnow = datetime.now(tz=pytz.UTC)
        delta = utcnow - form.creation_date
        print(delta)
        assert delta.total_seconds() < 3

    def test_owner_name(self):
        from ksweb.model.questionary import _owner_name as on
        self.test_questionary_create()
        form = self._get_questionary_by_title('TestQuestionary')
        assert 'Lawyer' == on(form)

    def test_user_shared_with(self):
        from ksweb.model.questionary import _shared_with as sw
        self.test_questionary_create()
        form = self._get_questionary_by_title('TestQuestionary')
        assert u"lawyer1@ks.axantweb.com" == sw(form)


""" FIXME:
    def test_hack_response_multi(self):
        self._login_lavewr()
        workspace1 = self._get_workspace('Area 1')
        fake_advanced_precond = self._create_fake_advanced_precondition_red_animal("Advanced_precond")
        qa_color = self._get_qa_by_title('Favourite color')
        color_content = [
            {
                "content": "Il tuo colore preferito",
                "type": "text",
                "title": ""
            },
            {
                "content": str(qa_color._id),
                "type": "qa_response",
                "title": "Favourite Color"
            }
        ]
        out_1 = self._create_output("example1", workspace1._id, fake_advanced_precond._id, color_content)

        qa_animal = self._get_qa_by_title('Favourite color')
        animal_content = [
            {
                "content": "Ti piacciono gli animali: ",
                "type": "text",
                "title": ""
            },
            {
                "content": str(qa_animal._id),
                "type": "qa_response",
                "title": "Favourite Animals"
            }
        ]
        out_2 = self._create_output("example1", workspace1._id, fake_advanced_precond._id, animal_content)

        content = [
            {
                'type': "text",
                'content': "Hey! ",
                'title': ""
            },
            {
                'type': "output",
                'content': str(out_1._id),
                'title': out_1.title
            },
            {
                'type': "text",
                'content': "Other stuff",
                'title': ""
            },
            {
                'type': "output",
                'content': str(out_2._id),
                'title': out_2.title
            },
        ]
        document = self._create_document("Advanced_document", workspace1._id, content)
        questionary = self._create_questionary("Advanced_Questionary", document._id)

        resp = self.app.get('/questionary/compile.json', params={
            'id': str(questionary._id)
        }).json
        assert resp['quest_compiled']['completed'] is False, resp

        qa_response = {
            'Favourite color': {
                'response': 'Red',
                'status': 200
            },
            'Animal liked': {
                'response': 'Fake options',
                'status': 412
            }
        }
        rel_qa = self._get_qa(resp['quest_compiled']['qa'])

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': qa_response[rel_qa.title]['response']
        }, status=qa_response[rel_qa.title]['status']).json

        rel_qa = self._get_qa(resp['quest_compiled']['qa'])

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': qa_response[rel_qa.title]['response']
        }, status=qa_response[rel_qa.title]['status']).json
"""
