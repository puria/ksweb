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
        self.precond_values = {}

        for elem in self.document.content:
            if elem['type'] == "text":
                #  elem is like this: { "content" : "Simple text", "type" : "text", "title" : ""}
                self.document_values.append(elem['content'])
            elif elem['type'] == "output":
                #  elem is like this: {"content" : "575eb879c42d7518bb972256", "type" : "output", "title" : "ciao"}
                output_res = self.evaluate_output(elem['content'])
                #  If not yet completed, show the answer
                if not output_res['completed']:
                    output_res['document_generated'] = self.document_values
                    return output_res
            else:
                #  Insert for security evaluation
                raise Exception("Invalid document element type: %s" % elem)

        return {
            'completed': True,
            'document_generated': self.document_values
        }

    def evaluate_output(self, output_id):
        """
        Evaluated the related output
        :param output_id: id of the output
        :return:
        """
        from ksweb import model
        #  Check if the output is already evaluated
        #  If the output is already evaluated, simple getting the text of the evaluation
        if self.output_values.has_key(output_id):
            self.document_values.append(self.output_values[output_id]['evaluated_text'])
            return {'completed': True}

        #  We not have already evaluated the output, we must evaluate the related precondition
        output = model.Output.query.get(_id=ObjectId(output_id))
        precond = self.evaluate_precond(output.precondition)
        if precond['completed']:
            self._compile_output(output, self.precond_values[str(output._precondition)])
            self.document_values.append(self.output_values[output_id]['evaluated_text'])
            return {'completed': True}

        """
        In this case the precond is not completed and the return value is like this:
        {
            'completed': False,
            'qa': "575eb879c42d7518bb972256"
        }
        """
        return precond

    def _compile_output(self, output, precondition_value):
        """
        Questo metodo serve per salvare direttamente dell'output in chiaro nel risultato finale del questionario.
        :param output:
        :param precondition_value:
        """
        #  If the precondition is not valid, therefore the output is empty
        evaluated_text = ""
        if precondition_value:
            #  for each output content:
            #  if is text, insert directly
            #  if is a qa response, show the related response
            for elem in output.content:
                if elem['type'] == "text":
                    #  elem like this { "content" : "Simple text", "type" : "text", "title" : "" }
                    evaluated_text += elem['content']
                elif elem['type'] == "qa_response":
                    #  elem like this { "content" : "57723171c42d7513bb31e17d", "type" : "qa_response", "title" : "Colori" }
                    #  Getting the response of the qa
                    #  The user have already response to the answer oterwise is not possible evaluate the precondition
                    if isinstance(self.qa_values[elem['content']], basestring):
                        evaluated_text += self.qa_values[elem['content']]
                    else:
                        evaluated_text += ', '.join(self.qa_values[elem['content']])
                else:
                    #  Insert for security evaluation
                    raise Exception("Output elem type not valid: %s" % elem)

        self.output_values[str(output._id)] = {
            'evaluation': True,
            'evaluated_text': evaluated_text
        }

    def evaluate_precond(self, precondition):
        """
        Evaluate if the precondition is already evaluated or not.
        :param precondition: Precondition Object
        :return: completed: True if the precondition is already evaluated and in the precond field return the value of the precondition
        :return: completed: False if the precondition or more qas related are not already evaluated and in the qa field the qa id of the missing qa
        """
        if self.precond_values.has_key(str(precondition._id)):
            return {
                'completed': True,
                'precond': self.precond_values[str(precondition._id)]
            }

        qa_involved = precondition.response_interested
        #  Check if all qa involved have a response
        for qa_id in qa_involved.keys():
            if not qa_id in self.qa_values.keys():
                print "QA: %s not already responded" % qa_id
                return {'completed': False, 'qa': qa_id}

        #  Now all qa have response, we are able to evaluate the precondition
        prec_str = self._precondition_str_to_evaluate(precondition)
        res_eval = eval(prec_str)
        self.precond_values[str(precondition._id)] = res_eval

        return {
            'completed': True,
            'precond': res_eval
        }

    def _precondition_str_to_evaluate(self, precondition):
        """
        Return an evaluation string for evaluate the precondition
        :param precondition:
        :return: string for process the evaluation
        """
        from ksweb import model

        str_to_eval = ""
        if precondition.type == 'simple':
            if precondition.simple_text_response:
                str_to_eval = "'%s' != ''" % self.qa_values[str(precondition.condition[0])]
            else:
                response_of_precondition = self.qa_values[str(precondition.condition[0])]
                #  Check if response is only one as text for example 'red'
                #  Cast this as list for uniform the string evaluation process
                if isinstance(response_of_precondition, basestring):
                    response_of_precondition = [response_of_precondition]

                for i in response_of_precondition[:-1]:
                    str_to_eval += "'%s' == '%s' or " % (precondition.condition[1], i)

                str_to_eval += "'%s' == '%s'" % (precondition.condition[1], response_of_precondition[-1])

        elif precondition.type == 'advanced':
            for cond in precondition.condition:
                if cond in model.Precondition.PRECONDITION_OPERATOR:
                    str_to_eval += "%s " % cond
                else:
                    related_precondition = model.Precondition.query.find({'_id': ObjectId(cond)}).first()
                    #  Getting the evaluation string of this precondition
                    str_to_eval += self._precondition_str_to_evaluate(related_precondition)
        return str_to_eval


__all__ = ['Questionary']
