# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
from bson import ObjectId
from tg import expose, redirect, validate, flash, url, RestController, decode_params, validation_errors_response, \
    request, response

# from tg.i18n import ugettext as _
# from tg import predicates

# from ksweb.model import DBSession
from tw2.core import OneOfValidator, LengthValidator, StringLengthValidator

from ksweb import model
from ksweb.lib.validator import QAExistValidator


class PreconditionSimpleController(RestController):

    @expose('ksweb.templates.precondition/simple')
    def new(self, **kw):
        return dict(page='precondition/simple-index')

    @expose('ksweb.templates.precondition.simple.new')
    def new(self, **kw):
        return dict(page='precondition-new')

    @decode_params('json')
    @expose('json')
    @validate({
        'question': QAExistValidator(required=True),
        'answer_type': OneOfValidator(values=[u'have_response', u'what_response'], required=True),
        #'interested_response': LengthValidator(required=False),
        'title': StringLengthValidator(min=4),
    }, error_handler=validation_errors_response)
    def post(self, question, answer_type, interested_response, title,  **kw):

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
                title=title,
                type='simple',
                condition=[ObjectId(question), interested_response[0]]
            )
        else:
            #  CASO AVANZATO sono state selezionate piu' risposte, devo prima creare tutte le precondizioni semplici e poi creare quella complessa

            if answer_type == "have_response":
                print "have_response"
                interested_response = model.Qa.query.get(_id=ObjectId(question)).answers

                #  Devo creare una precondizione semplice per ogni possibile risposta alla domanda
                #  Creare una precondizione complessa che utilizzi tutte le precondizioni semplici e le metta in or

            if answer_type == "what_response":
                print "what_response"
                #  Devo creare una precondizione semplice per ogni risposta selezionata della domanda
                #  Creare una precondizione complessa che utilizzi tutte le precondizioni semplici e le metta in or

                if len(interested_response) <= 1:
                    response.status_code = 412
                    return dict(
                        errors={'interested_response': 'Inserire almeno una risposta'})


            base_precond = []
            for resp in interested_response:
                prec = model.Precondition(
                    _owner=user._id,
                    title="_base_for_%s" % title,
                    type='simple',
                    condition=[ObjectId(question), resp],

                    public=True,
                    visible=False
                )
                base_precond.append(prec)
            res = []
            for prc in base_precond[:-1]:
                res.append(prc._id)
                res.append('|')

            res.append(base_precond[-1]._id)

            model.Precondition(
                _owner=user._id,
                title=title,
                type='advanced',
                condition=res
            )

        return dict(errors=None)
