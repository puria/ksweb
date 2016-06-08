# -*- coding: utf-8 -*-
"""Qa controller module"""
from bson import ObjectId
from tg import expose, redirect, validate, flash, url, validation_errors_response, response, RestController, \
    decode_params, request
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates

from tw2.core import StringLengthValidator, OneOfValidator

from ksweb import model
from ksweb.lib.validator import CategoryExistValidator


class QaController(RestController):
    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.qa.index')
    def get_all(self, **kw):
        return dict(page='qa-index')

    @expose('json')
    @expose('ksweb.templates.qa.new')
    def new(self, **kw):
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=4),
        'category': CategoryExistValidator(required=True),
        'question': StringLengthValidator(min=4),
        'tooltip': StringLengthValidator(min=0, max=100),
        'link': StringLengthValidator(min=0, max=100),
        'answer_type': OneOfValidator(values=model.Qa.QA_TYPE, required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, category, question, tooltip, link, answer_type, answers=None, **kw):

        if answer_type == "single" or answer_type == "multi":
            if len(answers) < 2:
                response.status_code = 412
                return dict(
                    errors={'answers': 'Inserire almeno due risposte'})

        user = request.identity['user']

        model.Qa(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            question=question,
            tooltip=tooltip,
            link=link,
            type=answer_type,
            answers=answers,
            public=True,
            visible=True
        )
        return dict(errors=None)
