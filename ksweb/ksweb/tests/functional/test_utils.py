# -*- coding: utf-8 -*-
import datetime
import json

from bson import ObjectId
from ksweb.lib.utils import to_object_id, upsert_document, clone_obj, find_entities_from_html
from ksweb.model import Qa, DBSession
from ksweb.tests import TestController
from ksweb import model


class TestUtils(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self._login_admin()
        self.ws = self._get_workspace('Area 1')
        self.document = {'qa': {}, 'advanced_preconditions': {}, 'simple_preconditions': {}, 'outputs': {}}
        self.qa = self._create_qa('title', self.ws._id, 'question', 'tooltip', 'link', 'single', ['a', 'b'])
        self.qa_struct = {str(self.qa._id): {'_parent_precondition': None, 'title': u'title', 'question': u'question',
                                             'tooltip': u'tooltip', 'status': None,
                                             'visible': True, 'link': u'link', 'answers': [u'a', u'b'],
                                             '_id': ObjectId(self.qa._id),
                                             'auto_generated': False,
                                             'type': u'single', 'public': True}
                          }
        self.qa_multi = self._create_qa('title1', self.ws._id, 'question1', 'tooltip1', 'link1', 'multi', ['a', 'b'])
        self.qa_multi_struct = {
            str(self.qa_multi._id): {'_parent_precondition': None, 'title': u'title1', 'question': u'question1',
                                     'tooltip': u'tooltip1', 'status': None, 'auto_generated': False,
                                     'visible': True, 'link': u'link1', 'answers': [u'a', u'b'],
                                     '_id': ObjectId(self.qa_multi._id),
                                     'type': u'multi', 'public': True}
        }
        self.prec = self._create_simple_precondition('title', self.ws._id, self.qa._id, interested_response=['a'])
        self.prec_struct = {str(self.prec._id): {'title': u'title', 'visible': True, '_id': ObjectId(self.prec._id),
                                                 'type': u'simple', 'public': True, 'status': None,
                                                 'auto_generated': False,
                                                 'condition': [ObjectId(self.qa._id), u'a']}}
        self.imported_document = json.load(open('ksweb/tests/functional/document_to_import.json'))
        self.imported_document_advanced = json.load(open('ksweb/tests/functional/document_to_import_advanced.json'))

    # def test_export_qa_simple(self):
    #     self._login_admin()
    #     export_qa(self.qa._id, self.document)
    #     assert self.document['qa'] == self.qa_struct, self.document['qa']
    #
    # def test_export_qa_multi(self):
    #     self._login_admin()
    #     export_qa(self.qa_multi._id, self.document)
    #     assert self.document['qa'] == self.qa_multi_struct, ('>>>>>', self.document['qa'], self.qa_multi_struct, '<<<<<')
    #
    # def test_export_qa_text(self):
    #     self._login_admin()
    #     qa = self._create_qa('title2', self.ws._id, 'question2', 'tooltip2', 'link2', 'text', None)
    #     export_qa(qa._id, self.document)
    #     expected = {str(qa._id): {'_parent_precondition': None, 'title': u'title2', 'question': u'question2',
    #                               'tooltip': u'tooltip2', u'status': None, 'auto_generated': False,
    #                               'visible': True, 'link': u'link2', 'answers': None, '_id': ObjectId(qa._id),
    #                               'type': u'text', 'public': True}
    #                 }
    #     assert self.document['qa'] == expected, self.document['qa']
    #
    # def test_export_simple_precondition(self):
    #     self._login_admin()
    #     export_preconditions(precondition_id=self.prec._id, document=self.document)
    #     assert self.document['qa'] == self.qa_struct, self.document['qa']
    #     assert self.document['simple_preconditions'] == self.prec_struct, self.document['simple_preconditions']
    #
    # def test_export_advanced_precondition(self):
    #     self._login_admin()
    #     conditions = [
    #         {
    #             'type': 'precondition',
    #             'content': str(self.prec._id)
    #         },
    #         {
    #             'type': 'operator',
    #             'content': 'or'
    #         },
    #         {
    #             'type': 'precondition',
    #             'content': str(self.prec._id)
    #         }
    #     ]
    #
    #     a_prec = self._create_advanced_precondition('title2', workspace_id=self.ws._id, conditions=conditions)
    #     export_preconditions(a_prec._id, self.document)
    #     assert self.document['qa'] == self.qa_struct, self.document['qa']
    #     assert self.document['simple_preconditions'] == self.prec_struct, self.document['simple_preconditions']
    #     expected = {str(a_prec._id): {'title': u'title2', 'visible': True, '_id': ObjectId(a_prec._id), 'auto_generated': False,
    #                                   'type': u'advanced', 'public': True, 'auto_generated': False, 'status': None,
    #                                   'condition': [ObjectId(self.prec._id), u'or', ObjectId(self.prec._id)]}}
    #     assert self.document['advanced_preconditions'] == expected, (self.document['advanced_preconditions'], expected)
    #
    # def test_export_output(self):
    #     self._login_admin()
    #     o = self._create_output('output', self.ws._id, self.prec._id, html='@{%s}' % self.qa._id)
    #     o1 = self._create_output('output1', self.ws._id, self.prec._id, html='@{%s} #{%s}' % (self.qa._id, o._id))
    #     export_outputs(o1._id, self.document)
    #     assert self.document['qa'] == self.qa_struct, self.document['qa']
    #     assert self.document['simple_preconditions'] == self.prec_struct, self.document['simple_preconditions']
    #
    #     expect = {'auto_generated': False,
    #               'content': [
    #                   {'type': 'output', 'content': '%s' % o._id, 'title': 'output'},
    #                   {'type': 'qa_response', 'content': '%s' % self.qa._id, 'title': 'title'}],
    #               'html': '@{%s} #{%s}' % (self.qa._id, o._id),
    #               'visible': True,
    #               '_id': o1._id,
    #               'public': True,
    #               'title': 'output1',
    #               '_precondition': self.prec._id,
    #               'status': 'UNREAD'}
    #
    #     assert self.document['outputs'][str(o1._id)] == expect, (expect, self.document['outputs'][str(o1._id)])

    def test_to_object_id(self):
        o = to_object_id("507f1f77bcf86cd799439011")
        assert isinstance(o, ObjectId), type(o)

    def test_to_object_id_none(self):
        o = to_object_id(None)
        assert o is None, o

    def test_upsert_document(self):
        inserted = upsert_document(cls=model.Qa,
                                   _owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id),
                                   _workspace=ObjectId(self.ws._id),
                                   _parent_precondition=None,
                                   title='title 4',
                                   question='question',
                                   tooltip='tooltip',
                                   link='link',
                                   type='text',
                                   answers=['answers'],
                                   public=True,
                                   visible=True)
        DBSession.flush_all()
        assert isinstance(inserted, Qa), type(inserted)
        fetched = Qa.query.find({'title': 'title 4'}).all()
        assert inserted in fetched, fetched
        qas = model.Qa.query.find().all()
        assert len(qas) == 3, qas

    def test_upsert_document_already_in(self):
        qa = Qa(_owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id),
                _workspace=ObjectId(self.ws._id),
                _parent_precondition=None,
                title='title',
                question='question',
                tooltip='tooltip',
                link='link',
                type='text',
                answers=['answers'],
                public=True,
                visible=True)
        model.DBSession.flush_all()

        inserted = upsert_document(cls=model.Qa, _owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id),
                                   _workspace=ObjectId(self.ws._id),
                                   _parent_precondition=None,
                                   title='title',
                                   question='question',
                                   tooltip='tooltip',
                                   link='link',
                                   type='text',
                                   answers=['answers'],
                                   public=True,
                                   visible=True)
        assert inserted is qa, (inserted, qa)
        qas = model.Qa.query.find().all()
        assert len(qas) == 3, qas

    def test_clone_obj(self):
        precondition = self._create_fake_simple_precondition('blah blah')
        qa = self._get_or_create_qa('title')
        qa.parent_precondition = precondition
        qa_cloned = clone_obj(Qa, qa, {'link': 'linkssss'})

        assert qa_cloned.title == 'title'
        assert qa_cloned.link == 'linkssss'
        assert qa_cloned._id != qa._id

    def test_empty_find_entities_from_html(self):
        o, q = find_entities_from_html(None)
        assert isinstance(o, list)
        assert isinstance(q, list)

    # def test_import_qa(self):
    #     imported_id = import_qa(imported_document=self.imported_document, qa_id='5922a961c42d753c2d93263f',
    #                             workspace_id=ObjectId(self.ws._id),
    #                             owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id))
    #
    #     qa_expected = self.imported_document['qa']['5922a961c42d753c2d93263f']
    #
    #     fetched = Qa.query.find({'_id': imported_id}).first()
    #     assert fetched.title == qa_expected['title'], fetched.title
    #     assert fetched.answers == qa_expected['answers'], fetched.answers
    #
    # def test_import_qa_with_precondition(self):
    #     imported_id = import_qa(imported_document=self.imported_document, qa_id='5922a9bec42d753c2d932658',
    #                             workspace_id=ObjectId(self.ws._id),
    #                             owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id))
    #
    #     qa_imported = self.imported_document['qa']['5922a9bec42d753c2d932658']
    #     prec_expected = self.imported_document['simple_preconditions'][qa_imported['_parent_precondition']]
    #     qa_expected = self.imported_document['qa'][prec_expected['condition'][0]]
    #
    #     fetched = Qa.query.find({'_id': imported_id}).first()
    #     assert fetched.title == qa_imported['title'], fetched.title
    #     assert fetched.answers ==qa_imported['answers'], fetched.answers
    #
    #     prec_fetched = model.Precondition.query.find({'title': prec_expected['title']}).first()
    #     assert prec_fetched.type == prec_expected['type'], prec_fetched.type
    #
    #     qa_fetched = Qa.query.find({'title': qa_expected['title']}).first()
    #     assert qa_fetched.answers == qa_expected['answers'], qa_fetched.title

    # def test_import_precondition_or(self):
    #     prec = import_precondition(imported_document=self.imported_document, precondition_id='or',
    #                                workspace_id=ObjectId(self.ws._id),
    #                                owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id))
    #     assert prec == 'or', prec
    #
    # def test_import_advanced_precondition(self):
    #     imported_prec = import_precondition(imported_document=self.imported_document_advanced,
    #                                         precondition_id='5926ad39c42d75ff9668f281',
    #                                         workspace_id=ObjectId(self.ws._id),
    #                                         owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id))
    #     prec_expected = self.imported_document_advanced['advanced_preconditions']['5926ad39c42d75ff9668f281']
    #     simple_to_insert_1 = self.imported_document_advanced['simple_preconditions'][prec_expected['condition'][0]]
    #     simple_to_insert_2 = self.imported_document_advanced['simple_preconditions'][prec_expected['condition'][2]]
    #
    #     prec_fetched = model.Precondition.query.find({'title': prec_expected['title']}).first()
    #
    #     assert prec_fetched.type == prec_expected['type'], prec_fetched.type
    #     assert isinstance(prec_fetched.condition, list), type(prec_fetched.condition)
    #
    #     simple_fetched = model.Precondition.query.find({'title': simple_to_insert_1['title']}).first()
    #     assert simple_fetched.type == simple_to_insert_1['type'], simple_fetched.type
    #
    #     simple_fetched = model.Precondition.query.find({'title': simple_to_insert_2['title']}).first()
    #     assert simple_fetched.type == simple_to_insert_2['type'], simple_fetched.type
    #
    # def test_import_output(self):
    #     imported_out = import_output(imported_document=self.imported_document_advanced, output_id='5926ad64c42d75ff9668f290',
    #                                  workspace_id=ObjectId(self.ws._id), owner=ObjectId(self._get_user('lawyer1@ks.axantweb.com')._id))
    #
    #     out_expected = self.imported_document_advanced['outputs']['5926ad64c42d75ff9668f290']
    #     out_fetched = model.Output.query.find({'title': out_expected['title']}).first()
    #     assert out_fetched.html != out_expected['html'], out_fetched.html
    #
    #     qa_expected = self.imported_document_advanced['qa'][out_expected['content'][1]['content']]
    #     out1_expected = self.imported_document_advanced['outputs'][out_expected['content'][0]['content']]
    #
    #     qa_fetched = model.Qa.query.find({'title': qa_expected['title']}).first()
    #     assert qa_fetched.question == qa_expected['question'], (qa_fetched.question, qa_expected['question'])
    #     out1_fetched = model.Output.query.find({'title': out1_expected['title']}).first()
    #     assert out1_fetched.visible == out1_expected['visible'], (out1_fetched.visible, out1_expected['visible'])
