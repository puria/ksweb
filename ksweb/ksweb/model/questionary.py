# -*- coding: utf-8 -*-
"""Questionary model module."""
import logging

import tg
from bson import ObjectId
from ksweb.model import DBSession, Document, User, Output, Precondition, Qa
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass

try:
    basestring
except NameError:
    basestring = str

log = logging.getLogger(__name__)


def _compile_questionary(obj):
    workspace = Document.query.find({'_id': ObjectId(obj._document)}).first()._category
    return Markup("<a href='%s'>%s</a>" % (tg.url('/questionary/compile', params=dict(_id=obj._id, workspace=workspace)),
                                           obj.title))


def _owner_name(o):
    return User.query.find({'_id': o._owner}).first().display_name


def _shared_with(o):
    return User.query.find({'_id': o._user}).first().email_address


class Questionary(MappedClass):
    __ROW_COLUM_CONVERTERS__ = {
        'title': _compile_questionary,
        '_owner': _owner_name,
        '_user': _shared_with,
    }

    class __mongometa__:
        session = DBSession
        name = 'questionaries'
        indexes = [
            ('_user',),
            ('_owner',),
            ('_document',),
        ]

    _id = FieldProperty(s.ObjectId)

    title = FieldProperty(s.String, required=False)

    #  User is the the target of the questionary
    _user = ForeignIdProperty('User')
    user = RelationProperty('User')

    #  Owner is the owner of the questionary who send id to the user
    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    #  Document is the related document
    _document = ForeignIdProperty('Document')
    document = RelationProperty('Document')

    completed = FieldProperty(s.Bool, if_missing=False)
    expressions = FieldProperty(s.Anything, if_missing={})
    output_values = FieldProperty(s.Anything, if_missing={})
    """
    Is a nested dictionary with:
    key: Obj(id) of the related output
    value:
        evaluation: Boolean evaluation of the related precondition, for determinate if show,
                    or hide the related output text
        evaluated_text: Text of the related output when is evaluated
    """

    precond_values = FieldProperty(s.Anything, if_missing={})
    """
    Is a dictionary with:
    key: Obj(id) of the precondition
    value: Boolean evaluation of the precondition
           True: if true
           False: if False
           None: if is not yet processed
    """

    qa_values = FieldProperty(s.Anything, if_missing={})
    """
    Is a dictionary with:
    key: Obj(id) of the qa
    value:
        In case of text or single response of the qa, the response are simply text.
        In case of multiple response of the qa, the response is a list with ['Res1', 'Resp4']
    """

    @property
    def creation_date(self):
        return self._id.generation_time

    @property
    def completion(self):
        if self.completed:
            return "100 %"
        if not len(self.expressions):
            return "0 %"
        return "%d %%" % int(len(self.qa_values)*1.0/len(self.expressions)*100)

    @property
    def evaluate_questionary(self):
        # self.document_values = []
        self.output_values = {}
        self.generate_expression()

        if not self.document.content:
            return {'completed': False}
        # document contains outputs only
        for output in self.document.content:
            output_id = output['content']
            output_res = self.evaluate_expression(output_id)

            if not output_res['completed']:
                return output_res
            else:
                if self.output_values[output_id].get('evaluation'):
                    res = self.compile_output(output_id)
                    # this need for to show other questions though output is already evaluated,
                    # for example when output uses some response to a certain questions
                    if res:
                        return res
        self.completed = True
        return {
            'completed': True
        }

    def generate_expression(self):
        if not self.document.content:
            self.expressions = []
            return
        for o in self.document.content:
            output = Output.query.get(_id=ObjectId(o['content']))
            self.expressions[str(output._id)] = self._generate(output.precondition)

    def _generate(self, precondition):
        parent_expression, expression = '', ''
        if not precondition:
            return "()"

        if precondition.is_simple:
            qa = precondition.get_qa()

            if qa._parent_precondition:
                parent_expression = '(' + self._generate(qa.parent_precondition) + ') and '
            if precondition.simple_text_response:
                expression = "q_%s != ''" % str(precondition.condition[0])
            elif precondition.single_choice_response:
                expression = "q_%s == %s" % (str(precondition.condition[0]),
                                             repr(precondition.condition[1]))
            elif precondition.multiple_choice_response:
                expression = "%s in q_%s" % (str(repr(precondition.condition[1])),
                                             precondition.condition[0])
            return parent_expression + expression
        else:
            advanced_expression = ""
            for item in precondition.condition:
                if isinstance(item, basestring):
                    advanced_expression += ' %s ' % item
                elif isinstance(item, ObjectId):
                    p = Precondition.query.get(_id=item)
                    advanced_expression += '( %s )' % self._generate(p)

        return advanced_expression

    def compile_output(self, output_id):
        from . import Output
        output = Output.query.get(_id=ObjectId(output_id))

        for elem in output.content:
            if elem['type'] == "qa_response":
                content = self.qa_values.get(elem['content'])
                if not content:
                    # no answer found for this question
                    return {'qa': elem['content']}
            elif elem['type'] == 'output':  # nested output
                output_nested_id = elem['content']
                output_nested = Output.query.get(_id=ObjectId(output_nested_id))
                if output_nested.precondition:
                    self.expressions[str(output_nested_id)] = self._generate(output_nested.precondition)
                    output_res = self.evaluate_expression(output_nested_id)
                else:
                    log.error(output_nested)
                    log.error(elem['content'])
                if not output_res['completed']:
                    return output_res
                else:
                    if self.output_values[output_nested_id].get('evaluation'):
                        res = self.compile_output(output_nested_id)
                        # this need for to show other questions though output is already evaluated,
                        # for example when output uses some response to a certain questions
                        if res:
                            return res
        return None

    def evaluate_expression(self, output_id):
        expression = self.expressions[output_id]
        answers = dict()

        for _id, resp in self.qa_values.items():
            answer = resp['qa_response']
            if isinstance(answer, basestring):
                answers['q_' + _id] = answer
            else:
                # lists
                answers['q_' + _id] = "[%s]" % ' ,'.join(map(lambda x: "'%s'" % x, answer))

        try:
            evaluation = eval(expression, answers)
        except NameError as ne:
            message = str(getattr(ne, 'message', ne))
            _id = message.split("'")[1][2:]
            return {
                'completed': False,
                'qa': _id
            }

        self.output_values[output_id] = {
            'evaluation': evaluation
        }

        return {
            'completed': True
        }

    @property
    def answers(self):
        questions = sorted(self.qa_values.items(), key=lambda i: i[1].order_number)
        return [dict(question=Qa.query.get(_id=ObjectId(q)).question, answer=a.qa_response) for q, a in questions]


__all__ = ['Questionary']
