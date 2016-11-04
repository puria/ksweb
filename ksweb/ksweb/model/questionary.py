# -*- coding: utf-8 -*-
"""Questionary model module."""
from bson import ObjectId
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass

from ksweb.model import DBSession
import tg


def _compile_questionary(obj):
    return Markup("<a href='%s'>%s</a>" % (tg.url('/questionary/compile', params=dict(_id=obj._id)), obj.title))


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

    document_values = FieldProperty(s.Anything, if_missing=[])
    """
    A list with a compiled document values
    """

    expressions = FieldProperty(s.Anything, if_missing={})

    output_values = FieldProperty(s.Anything, if_missing={})
    """
    Is a nested dictionary with:
    key: Obj(id) of the related output
    value:
        evaluation: Boolean evaluation of the related precondition, for determinate if show, or hide the related output text
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
        """
        Valutazione del questionario, ogni volta svuoto i valori delle valutazioni di documenti, output e precond,
        così nel caso venga riaperto il questionario dopo che è stata inserita una nuova domanda,
        viene ricalcolato tutto e sarà aggiornato.
        Va a recuperare il documento collegato e ne analizza tutto il content
        :return: Se a tutti gli output del content sono stati valutati restituisce come stato completed: True
        :return: Se invece non sono stati ancora valutati degli output restituisce come stato completed: False e la qa alla quale bisogna rispondere
        """

        self.document_values = []
        self.output_values = {}
        self.generate_expression()

        print "========================================================================="
        print "evaluate_questionary"
        print "========================================================================="
        print ""

        for elem in self.document.content:
            if elem['type'] == "text":
                self.document_values.append(elem['content'])
            elif elem['type'] == "output":
                output_id = elem['content']
                output_res = self.evaluate_expression(output_id)
                if not output_res['completed']:
                    print "Output", output_id, 'is NOT completed'
                    output_res['document_generated'] = self.document_values
                    return output_res
                else:
                    print "Output", output_id, 'is completed'
                    if self.output_values[output_id].get('evaluation'):

                        res = self.compile_output(output_id)
                        if res:
                            print "quiiiiiiiiiiiiiiiii"
                            return res
                    else:
                        print "Output", output_id, 'precondition failed'

        return {
            'completed': True,
            'document_generated': self.document_values
        }

    def generate_expression(self):
        from . import Output

        for elem in self.document.content:
            if elem['type'] == 'output':
                output = Output.query.get(_id=ObjectId(elem['content']))
                self.expressions[str(output._id)] = self._generate(output.precondition)

    def _generate(self, precondition):
        parent_expression, expression= '', ''

        if precondition.is_simple:
            qa = precondition.get_qa()

            if qa._parent_precondition:
                parent_expression = '(' + self._generate(qa.parent_precondition) + ') and '

            if precondition.simple_text_response:
                # TODO test
                expression = "q_%s != ''" % str(precondition.condition[0])
            elif precondition.single_choice_response:
                expression = "q_%s == '%s'" % (str(precondition.condition[0]), precondition.condition[1])
            elif precondition.multiple_choice_response:
                expression = "'%s' in q_%s" % (str(precondition.condition[1]), precondition.condition[0])

            return parent_expression + expression

        else:
            advanced_expression = ""
            for item in precondition.condition:
                if isinstance(item, basestring):
                    advanced_expression += ' %s ' % item
                elif isinstance(item, ObjectId):
                    from . import Precondition
                    p = Precondition.query.get(_id=item)
                    advanced_expression += ' %s ' % self._generate(p)



            print "END of PA",
            print advanced_expression
        return advanced_expression

    def compile_output(self, output_id):
        """
        Questo metodo serve per salvare direttamente dell'output in chiaro nel risultato finale del questionario.
        :param output:
        :param precondition_value:
        """
        from . import Output
        output = Output.query.get(_id=ObjectId(output_id))

        evaluated_text = ""

        for elem in output.content:
            if elem['type'] == "text":
                evaluated_text += elem['content']
            elif elem['type'] == "qa_response":
                # FIXME
                content = self.qa_values.get(elem['content'])
                if content:
                    if isinstance(content, basestring):
                        evaluated_text += self.qa_values[elem['content']]
                    else:
                        evaluated_text += ', '.join(self.qa_values[elem['content']])
                else:
                    return {'qa': elem['content']}

        self.document_values.append(evaluated_text)
        return None

    def evaluate_expression(self, output_id):

        print "========================================================================="
        print "output:", output_id

        expression = self.expressions[output_id]

        answers = dict()
        for _id, resp in self.qa_values.items():
            if isinstance(resp, basestring):
                answers['q_' + _id] = resp
            else:
                # array
                answers['q_' + _id] = "[%s]" % ' ,'.join(map(lambda x: "'%s'" % x, resp))



        try:
            print expression
            print "answers", answers

            evaluation = eval(expression, answers)
            print evaluation
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
