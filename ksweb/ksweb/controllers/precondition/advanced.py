# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
from bson import ObjectId
from tg import expose, redirect, validate, flash, url, RestController, decode_params, validation_errors_response, \
    request, response, tmpl_context

# from tg.i18n import ugettext as _
# from tg import predicates

from tw2.core import LengthValidator, StringLengthValidator

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
        operator_accepted=['and', 'or', 'not', '(', ')']

        bool_str = ""
        condition = []

        for cond in conditions:
            if cond['type'] == 'precondition':
                #  Check if precondition exist
                precond = model.Precondition.query.get(_id=ObjectId(cond['content']))
                if not precond:
                    response.status_code = 412
                    return dict(errors={'conditions': 'Precondizione non trovata.'})

                bool_str += "True "
                condition.append(ObjectId(cond['content']))

            elif cond['type'] == 'operator':
                if not cond['content'] in operator_accepted:
                    response.status_code = 412
                    return dict(errors={'conditions': 'Operatore logico non valido.'})

                bool_str += cond['content']+" "
                condition.append(cond['content'])

            else:
                response.status_code = 412
                return dict(errors={'conditions': 'Operatore non valido'})

        try:
            res_eval = eval(bool_str)
        except SyntaxError as e:
            response.status_code = 412
            return dict(errors={'conditions': 'Errore di sinstassi.'})

        user = request.identity['user']
        model.Precondition(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            type='advanced',
            condition=condition
        )

        return dict(errors=None)
