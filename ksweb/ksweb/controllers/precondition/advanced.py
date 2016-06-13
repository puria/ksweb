# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
from bson import ObjectId
from tg import expose, redirect, validate, flash, url, RestController, decode_params, validation_errors_response, \
    request, response, tmpl_context

# from tg.i18n import ugettext as _
# from tg import predicates

from tw2.core import OneOfValidator, LengthValidator, StringLengthValidator

from ksweb import model
from ksweb.lib.validator import CategoryExistValidator


class PreconditionAdvancedController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"
        tmpl_context.sidebar_precondition_advanced = "preconditions-advanced"


    @expose('ksweb.templates.precondition.advanced.new')
    def new(self, **kw):
        return dict()

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=4),
        'category': CategoryExistValidator(required=True),
        'conditions': LengthValidator(min=1, required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, category, conditions, **kw):
        print "title: %s" % title
        print "category: %s" % category
        print "kw: %s" % kw
        #  Fare scrematura di argomenti per evitare di eseguire del codice python potenzialmente dannoso
        #  Fare eval
        #  Se tutto ok ok vuol dire che va bene altrimenti errori

        option_type=['precondition', 'operator']
        operator_accepted=['and', 'or', 'not', '(', ')']

        '''
        {u'content': u'575581e4c42d75124a0a9602', u'type': u'precondition', u'key': 1, u'title': u'Ha risposto a domanda2'}
        {u'content': u'or', u'img_uri': u'/img/or_dark.png', u'type': u'operator', u'key': 2}
        {u'content': u'575581e4c42d75124a0a9601', u'type': u'precondition', u'key': 3, u'title': u'Ha risposto a domanda1'}
        '''

        bool_str = ""
        condition = []

        for cond in conditions:
            print cond
            if cond['type'] == 'precondition':
                #  Check if precondition exist
                print "verify precondition id"
                precond = model.Precondition.query.get(_id=ObjectId(cond['content']))
                print precond
                if not precond:
                    response.status_code = 412
                    return dict(errors={'conditions': 'Precondizione non trovata.'})

                bool_str += "True "
                condition.append(ObjectId(cond['content']))

            elif cond['type'] == 'operator':
                print "verify operator"
                #  Check if operator is valid
                if not cond['content'] in operator_accepted:
                    response.status_code = 412
                    return dict(errors={'conditions': 'Operatore logico non valido.'})

                bool_str += cond['content']+" "
                condition.append(cond['content'])

            else:
                print "not valid type"
                return "error"
        try:
            res_eval = eval(bool_str)
        except SyntaxError as e:
            response.status_code = 412
            return dict(errors={'conditions': 'Errore di sinstassi.'})

        print "eval: %s" % bool_str
        print "res: %s" % res_eval
        user = request.identity['user']

        model.Precondition(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            type='advanced',
            condition=condition
        )

        return dict(errors=None)
