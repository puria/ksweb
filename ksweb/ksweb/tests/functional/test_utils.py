# -*- coding: utf-8 -*-
from bson import ObjectId
from ksweb.lib.utils import export_qa, export_preconditions, export_outputs
from ksweb.tests import TestController
from ksweb import model


class TestUtils(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self._login_admin()
        self.ws = self._get_category('Categoria 1')
        self.document = {'qa': {}, 'advanced_preconditions': {}, 'simple_preconditions': {}, 'outputs': {}}
        self.qa = self._create_qa('title', self.ws._id, 'question', 'tooltip', 'link', 'single', ['a', 'b'])
        self.qa_struct = {str(self.qa._id): {'_parent_precondition': None, 'title': u'title', 'question': u'question',
                            'tooltip': u'tooltip',
                            'visible': True, 'link': u'link', 'answers': [u'a', u'b'], '_id': ObjectId(self.qa._id),
                            'type': u'single', 'public': True}
         }
        self.qa_multi = self._create_qa('title1', self.ws._id, 'question1', 'tooltip1', 'link1', 'multi', ['a', 'b'])
        self.qa_multi_struct = {str(self.qa_multi._id): {'_parent_precondition': None, 'title': u'title', 'question': u'question',
                                  'tooltip': u'tooltip',
                                  'visible': True, 'link': u'link', 'answers': [u'a', u'b'], '_id': ObjectId(self.qa_multi._id),
                                  'type': u'multi', 'public': True}
                    }
        self.prec = self._create_simple_precondition('title', self.ws._id, self.qa._id, interested_response=['a'])
        self.prec_struct = {str(self.prec._id): {'title': u'title', 'visible': True, '_id': ObjectId(self.prec._id),
                                                 'type': u'simple', 'public': True, 'condition': [ObjectId(self.qa._id), u'a']}}

    def test_export_qa_simple(self):
        self._login_admin()
        export_qa(self.qa._id, self.document)
        assert self.document['qa'] == self.qa_struct, self.document['qa']

    def test_export_qa_multi(self):
        self._login_admin()
        export_qa(self.qa_multi._id, self.document)
        assert self.document['qa'] == self.qa_multi_struct, self.document['qa']

    def test_export_qa_text(self):
        self._login_admin()
        qa = self._create_qa('title', self.ws._id, 'question', 'tooltip', 'link', 'text', None)
        export_qa(qa._id, self.document)
        expected = {str(qa._id): {'_parent_precondition': None, 'title': u'title', 'question': u'question',
                                  'tooltip': u'tooltip',
                                  'visible': True, 'link': u'link', 'answers': None, '_id': ObjectId(qa._id),
                                  'type': u'text', 'public': True}
                    }
        assert self.document['qa'] == expected, self.document['qa']

    def test_export_simple_precondition(self):
        self._login_admin()
        export_preconditions(precondition_id=self.prec._id, document=self.document)
        assert self.document['qa'] == self.qa_struct, self.document['qa']
        assert self.document['simple_preconditions'] == self.prec_struct, self.document['simple_preconditions']

    def test_export_advanced_precondition(self):
        self._login_admin()
        conditions = [
                {
                    'type': 'precondition',
                    'content': str(self.prec._id)
                },
                {
                    'type': 'operator',
                    'content': 'or'
                },
                {
                    'type': 'precondition',
                    'content': str(self.prec._id)
                 }
            ]

        a_prec = self._create_advanced_precondition('title2', category_id=self.ws._id, conditions=conditions)
        export_preconditions(a_prec._id, self.document)
        assert self.document['qa'] == self.qa_struct, self.document['qa']
        assert self.document['simple_preconditions'] == self.prec_struct, self.document['simple_preconditions']
        expected = {str(a_prec._id): {'title': u'title2', 'visible': True, '_id': ObjectId(a_prec._id),
                                      'type': u'advanced', 'public': True, 'condition': [ObjectId(self.prec._id), u'or',
                                                                                         ObjectId(self.prec._id)]}}
        assert self.document['advanced_preconditions'] == expected, (self.document['advanced_preconditions'], expected)

    def test_export_output(self):
        self._login_admin()
        content = [
            {'content': str(self.qa._id),
                     'type': 'qa_response',
                     'title': 'title'
            }
        ]
        o = self._create_output('output', self.ws._id, self.prec._id, content=content, html='html')

        content1 = [
            {'content': str(self.qa._id),
             'type': 'qa_response',
             'title': 'title'
             },
            {'content': str(o._id),
             'type': 'output',
             'title': 'output'
             }

        ]
        o1 = self._create_output('output1', self.ws._id, self.prec._id, content=content1, html='html')
        export_outputs(o1._id, self.document)
        assert self.document['qa'] == self.qa_struct, self.document['qa']
        assert self.document['simple_preconditions'] == self.prec_struct, self.document['simple_preconditions']
        expected = {'title': u'output1', 'content': [{u'content': str(self.qa._id),
                                                                                   u'type': u'qa_response',
                                                                                   u'title': u'title'},
                                                                                  {u'content': str(o._id),
                                                                                   u'type': u'output',
                                                                                   u'title': u'output'}
                                                                                  ],
                                                 'visible': True, 'html': u'html',
                                                 '_precondition': ObjectId(self.prec._id), '_id': ObjectId(o1._id),
                                                 'public': True}
        assert self.document['outputs'][str(o1._id)] == expected, (expected, self.document['outputs'][str(o1._id)])
