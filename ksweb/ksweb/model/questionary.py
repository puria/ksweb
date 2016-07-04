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
    return Markup("<a href='%s'>%s</a>" % (tg.url('/questionary/compile', params=dict(id=obj._id)), obj.title))


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
        Valutazione del questionario, ogni volta svuoto il contenuto dell'output come testo, così nel caso venga
        riaperto il questionario dopo che è stata inserita una nuova domanda, viene ricalcolato tutto e sarà
        aggiornato.
        Va a recuperare il documento collegato e ne analizza tutto il content
        Se a tutti gli output del content sono stati valutati restituisce come stato completed: True
        Se invece non sono stati ancora valutati degli output restituisce come stato completed: False e la qa alla quale bisogna rispondere
        :return:
        """

        #  Fix 1
        #  Svuoto il contenuto dell'output del questionario ogni volta che lo vado a valutare
        self.document_values = []

        res = {}
        for elem in self.document.content:
            if elem['type'] == "text":
                """
                elem is like this
                {
                    "content" : "Simple text",
                    "type" : "text",
                    "title" : ""
                }
                """
                self.document_values.append(elem['content'])
            elif elem['type'] == "output":
                """
                elem is like this
                {
                    "content" : "575eb879c42d7518bb972256",
                    "type" : "output",
                    "title" : "ciao"
                }
                """
                #  Now evaluate the related output
                output_res = self.evaluate_output(elem['content'])
                #  Se non risulta completato significa che devo mostrare una domanda
                if not output_res['completed']:
                    output_res['document_generated'] = self.document_values
                    return output_res
            else:
                print "Ignoring: %s" % elem
                continue

        return {
            'completed': True,
            'document_generated': self.document_values
        }

    # def evaluate_document(self):
    #     Inutile perche viene già svolto da evaluate_questionary
    #     Valuta il documento associato
    #     pass

    def evaluate_output(self, output_id):
        from ksweb import model
        #  Valuta output
        #  Verifico se ho già valutato questo output
        if self.output_values.has_key(output_id):
            #  Output already processed, simple getting the text of the evaluation
            print "Output already processed, simple getting the text of the evaluation"
            self.document_values.append(self.output_values[output_id]['evaluated_text'])
            return {'completed': True}

        #  Get the related output
        output = model.Output.query.get(_id=ObjectId(output_id))
        #  So che l'output non è stato ancora valutato perciò devo andare a valutare la precondizione associata
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
            #  Devo scorrere tutto il content dell'output:
            #  Se trovo del testo lo inserisco easy
            #  Se trovo la risposta a una domanda devo mostrare il valore della risposta
            for elem in output.content:
                if elem['type'] == "text":
                    """
                    elem like this
                    {
                        "content" : "Simple text",
                        "type" : "text",
                        "title" : ""
                    }
                    """
                    evaluated_text += elem['content']
                elif elem['type'] == "qa_response":
                    """
                    elem like this
                    {
                        "content" : "57723171c42d7513bb31e17d",
                        "type" : "qa_response",
                        "title" : "Colori"
                    }
                    """
                    #  L'utente ha già risposto alla domanda, vado a prendre il valore dai dati salvati,
                    #  Non mi devo preoccupare di chiedere vedere se ha risposto alla domanda, perchè questo mi è già
                    #  garantito dal fatto che altrimenti la precondizione non sarebbe stata verificata.
                    if isinstance(self.qa_values[elem['content']], basestring):
                        evaluated_text += self.qa_values[elem['content']]
                    else:
                        evaluated_text += ', '.join(self.qa_values[elem['content']])
                else:
                    print "Ignoring: %s" % elem
                    continue

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
        for qa_id in qa_involved.keys():
            if not qa_id in self.qa_values.keys():
                print "QA: %s not already responded" % qa_id
                return {
                    'completed': False,
                    'qa': qa_id
                }

        #  All qa have response, we are able to evaluate to the qa

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
        print "Analyzing precondition: %s" % precondition
        if precondition.type == 'simple':
            if precondition.simple_text_response:
            #if precondition.condition[1] == "":
                str_to_eval = "'%s' != ''" % self.qa_values[str(precondition.condition[0])]
            else:
                response_of_precondition = self.qa_values[str(precondition.condition[0])]
                if isinstance(response_of_precondition, basestring):
                    response_of_precondition = [response_of_precondition]
                for i in response_of_precondition:
                    str_to_eval = "'%s' == '%s'" % (precondition.condition[1], i)
                #str_to_eval = "'%s' == '%s'" % (precondition.condition[1], self.qa_values[str(precondition.condition[0])])
        elif precondition.type == 'advanced':
            for cond in precondition.condition:
                if cond in model.Precondition.PRECONDITION_OPERATOR:
                    str_to_eval += "%s " % cond
                else:
                    related_precondition = model.Precondition.query.find({'_id': ObjectId(cond)}).first()

                    str_to_eval += self._precondition_str_to_evaluate(related_precondition)
        else:
            return str_to_eval

        return str_to_eval

    #  Useless
    # def evaluate_qa(self, qa):
    #     """
    #     Evaluate if the qa have response or not.
    #     :param qa: Qa object
    #     :return: True or False, if return False return Qa
    #     """
    #     if self.qa_values.has_key(str(qa._id)):
    #         return {
    #             'completed': True
    #             }
    #     else:
    #         return {
    #             'completed': False,
    #             'qa': str(qa._id)
    #         }


__all__ = ['Questionary']
