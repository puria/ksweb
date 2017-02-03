# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model


class TestQuestionaryController(TestController):

    application_under_test = 'main'

    def test_access_permission_not_garanted(self):
        self.app.get('/questionary', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/questionary')
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lavewr()
        resp_lawyer = self.app.get('/questionary')
        assert resp_lawyer.status_code == 200

    def test_questionary_create(self):
        self._login_lavewr()
        doc = self._create_fake_document('Fake1')
        resp = self.app.post_json('/questionary/create', params={
            'questionary_title': 'TestQuestionary',
            'document_id': str(doc._id)
        })
        assert resp

    def test_compile_questionary(self):
        self._login_lavewr()
        questionary = self._create_fake_questionary('FakeQuestionary')
        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id)
        }).json
        assert resp['quest_compiled'] is not None, resp
        assert resp['quest_compiled']['completed'] is False, resp

    def test_responde_questionary(self):
        self._login_lavewr()
        questionary = self._create_fake_questionary('FakeQuestionary')
        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id)
        }).json
        assert resp['quest_compiled']['completed'] is False, resp

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': self.FAKE_RESPONSE[0]
        }).json

        assert resp['quest_compiled']['completed'] is True, resp

    def test_hack_response(self):
        self._login_lavewr()
        questionary = self._create_fake_questionary('FakeQuestionary')
        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id)
        }).json
        assert resp['quest_compiled']['completed'] is False, resp

        resp = self.app.post_json('/questionary/responde', params={
            '_id': str(questionary._id),
            'qa_id': resp['quest_compiled']['qa'],
            'qa_response': "Fake response"
        }, status=412).json

    #  TODO: Check/rewrite these test.
    """
    def test_compile_advanced_questionary(self):
        self._login_lavewr()
        category1 = self._get_category('Categoria 1')
        fake_advanced_precond = self._create_fake_advanced_precondition_red_animal("Advanced_precond")
        qa_color = self._get_qa_by_title('Favourite color')
        color_content = [
            {
                "content": str(qa_color._id),
                "type": "qa_response",
                "title": "Favourite Color"
            }
        ]
        out_1 = self._create_output("example1", category1._id, fake_advanced_precond._id, color_content)

        qa_animal = self._get_qa_by_title('Favourite color')
        animal_content = [
            {
                "content": str(qa_animal._id),
                "type": "qa_response",
                "title": "Favourite Animals"
            }
        ]
        out_2 = self._create_output("example1", category1._id, fake_advanced_precond._id, animal_content)

        content = [
            {
                'type': "output",
                'content': str(out_1._id),
                'title': out_1.title
            },
            {
                'type': "output",
                'content': str(out_2._id),
                'title': out_2.title
            },
        ]
        html = ''

        document = self._create_document("Advanced_document", category1._id, content, html)
        questionary = self._create_questionary("Advanced_Questionary", document._id)

        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id)
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
        self._login_lavewr()
        category1 = self._get_category('Categoria 1')
        fake_advanced_precond = self._create_fake_advanced_precondition_red_animal("Advanced_precond")
        qa_color = self._get_qa_by_title('Favourite color')
        color_content = [
            {
                "content": str(qa_color._id),
                "type": "qa_response",
                "title": "Favourite Color"
            }
        ]
        out_1 = self._create_output("example1", category1._id, fake_advanced_precond._id, color_content)

        qa_animal = self._get_qa_by_title('Favourite color')
        animal_content = [
            {
                "content": str(qa_animal._id),
                "type": "qa_response",
                "title": "Favourite Animals"
            }
        ]
        out_2 = self._create_output("example1", category1._id, fake_advanced_precond._id, animal_content)

        content = [
            {
                'type': "output",
                'content': str(out_1._id),
                'title': out_1.title
            },
            {
                'type': "output",
                'content': str(out_2._id),
                'title': out_2.title
            },
            {
                'type': "output",
                'content': str(out_1._id),
                'title': out_1.title
            },
        ]
        html = ''

        document = self._create_document("Advanced_document", category1._id, content, html) 
        questionary = self._create_questionary("Advanced_Questionary", document._id)

        resp = self.app.get('/questionary/compile.json', params={
            '_id': str(questionary._id)
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

        print "=====", resp

        assert resp['quest_compiled']['completed'] is True, resp

        # rel_qa = self._get_qa(resp['quest_compiled']['qa'])
        #
        # resp = self.app.post_json('/questionary/responde', params={
        #     '_id': str(questionary._id),
        #     'qa_id': resp['quest_compiled']['qa'],
        #     'qa_response': qa_response[rel_qa.title]['response']
        # }, status=qa_response[rel_qa.title]['status']).json
        #
        # assert resp['quest_compiled']['completed'] == True, resp


    def test_hack_response_multi(self):
        self._login_lavewr()
        category1 = self._get_category('Categoria 1')
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
        out_1 = self._create_output("example1", category1._id, fake_advanced_precond._id, color_content)

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
        out_2 = self._create_output("example1", category1._id, fake_advanced_precond._id, animal_content)

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
        document = self._create_document("Advanced_document", category1._id, content)
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