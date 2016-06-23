# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
from bson import ObjectId
from tg import expose, validate, RestController, decode_params, request, \
    validation_errors_response,  response, tmpl_context
from tw2.core import OneOfValidator, StringLengthValidator
from ksweb import model
from ksweb.lib.validator import QAExistValidator, CategoryExistValidator


class PreconditionSimpleController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"


    @expose('ksweb.templates.precondition.simple.new')
    def new(self, **kw):
        return dict(page='precondition-new')

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'question': QAExistValidator(required=True),
        'answer_type': OneOfValidator(values=[u'have_response', u'what_response'], required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, category, question, answer_type, interested_response,  **kw):

        print "question: %s" % question
        print "answer_type: %s" % answer_type
        print "interested_response: %s" % interested_response
        print "title: %s" % title
        print kw
        user = request.identity['user']

        #  CASO BASE in cui risco a creare una precondizione semplice per definizione e' quella di che venga solamente selezionata una risposta
        if len(interested_response) == 1:
            #  La risposta e' solo una creo una precondizione semplice
            print "Base case -> Simple Precondition"
            model.Precondition(
                _owner=user._id,
                _category=ObjectId(category),
                title=title,
                type='simple',
                condition=[ObjectId(question), interested_response[0]]
            )
        else:
            #  CASO AVANZATO sono state selezionate piu' risposte, devo prima creare tutte le precondizioni semplici e poi creare quella complessa
            if answer_type == "have_response":
                #  Create one precondition simple for all possibility answer to question
                #  After that create a complex precondition with previous simple precondition
                interested_response = model.Qa.query.get(_id=ObjectId(question)).answers

            if answer_type == "what_response":
                #  Create one precondition simple for all selected answer to question
                #  After that create a complex precondition with previous simple precondition

                if len(interested_response) <= 1:
                    response.status_code = 412
                    return dict(errors={'interested_response': 'Inserire almeno una risposta'})

            base_precond = []
            for resp in interested_response:
                prec = model.Precondition(
                    _owner=user._id,
                    _category=ObjectId(category),
                    title="_base_for_%s" % title,
                    type='simple',
                    condition=[ObjectId(question), resp],

                    public=True,
                    visible=False
                )
                base_precond.append(prec)

            condition = []
            for prc in base_precond[:-1]:
                condition.append(prc._id)
                condition.append('|')

            condition.append(base_precond[-1]._id)

            model.Precondition(
                _owner=user._id,
                _category=ObjectId(category),
                title=title,
                type='advanced',
                condition=condition
            )

        return dict(errors=None)
