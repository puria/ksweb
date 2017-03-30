# -*- coding: utf-8 -*-
"""Questionary model module."""
from bson import ObjectId
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass

from ksweb.model import DBSession
import tg
import logging

log = logging.getLogger(__name__)


def _compile_questionary(obj):
    return Markup("<a href='%s'>%s</a>" % (tg.url('/questionary/compile', params=dict(_id=obj._id))
                                           , obj.title))


class Questionary(MappedClass):
    __ROW_COLUM_CONVERTERS__ = {
        'title': _compile_questionary,
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

    # document_values = FieldProperty(s.Anything, if_missing=[])
    """
    A list with a compiled document values
    """

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
    def evaluate_questionary(self):
        log.debug("evaluate_questionary")
        """
        Valutazione del questionario, ogni volta svuoto i valori delle valutazioni di documenti,
        output e precond, così nel caso venga riaperto il questionario dopo che è stata inserita
        una nuova domanda, viene ricalcolato tutto e sarà aggiornato.
        Va a recuperare il documento collegato e ne analizza tutto il content
        :return: Se a tutti gli output del content sono stati valutati restituisce come stato
                 completed: True
        :return: Se invece non sono stati ancora valutati degli output restituisce come stato
                 completed: False e la qa alla quale bisogna rispondere
        """

        # self.document_values = []
        self.output_values = {}
        self.generate_expression()

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

        return {
            'completed': True
        }

    def generate_expression(self):
        log.debug("generate_expression")
        from . import Output
        for o in self.document.content:
            output = Output.query.get(_id=ObjectId(o['content']))
            self.expressions[str(output._id)] = self._generate(output.precondition)

    def _generate(self, precondition):
        log.debug("_generate")
        parent_expression, expression = '', ''

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
                    from . import Precondition
                    p = Precondition.query.get(_id=item)
                    advanced_expression += '( %s )' % self._generate(p)

        return advanced_expression

    def compile_output(self, output_id):
        log.debug("compile_output")

        """
        Questo metodo serve per salvare direttamente dell'output in chiaro nel risultato finale del
        questionario.

        Questo metodo appende all'array di stringhe document_values i vari componenti trovati nel
        documento, che siano testo semplice o risposte, un elemento per ogni cella dell'array

        :param output_id:

        """
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
                self.expressions[str(output_nested_id)] = self._generate(output_nested.precondition)
                output_res = self.evaluate_expression(output_nested_id)
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
        log.debug("evaluate_expression")

        expression = self.expressions[output_id]

        answers = dict()
        for _id, resp in self.qa_values.items():
            if isinstance(resp, basestring):
                answers['q_' + _id] = resp
            else:
                # array
                answers['q_' + _id] = "[%s]" % ' ,'.join(map(lambda x: "'%s'" % x, resp))
        try:
            evaluation = eval(expression, answers)
        except NameError as ne:
            _id = ne.message.split("'")[1][2:]
            return {
                'completed': False,
                'qa': _id
            }

        self.output_values[output_id] = {
            'evaluation': evaluation,
        }

        return {
            'completed': True
        }


__all__ = ['Questionary']
