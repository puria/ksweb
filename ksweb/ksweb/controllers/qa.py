# -*- coding: utf-8 -*-
"""Qa controller module"""
from bson import ObjectId
from tg import expose, redirect, validate, flash, url, validation_errors_response, response, RestController, \
    decode_params, request
# from tg.i18n import ugettext as _
# from tg import predicates
from tw2.core import StringLengthValidator, OneOfValidator

from ksweb import model
from ksweb.lib.base import BaseController
# from ksweb.model import DBSession
from ksweb.lib.validator import CategoryExistValidator


class QaController(RestController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = predicates.not_anonymous()

    @expose('ksweb.templates.qa.index')
    def get_all(self, **kw):
        return dict(page='qa-index')

    @expose('json')
    @expose('ksweb.templates.qa.new')
    def new(self, **kw):
        #return dict(page='qa-new')
        return dict(errors=None, values={'title':"titolo"})

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
    def post(self, title, category, question, tooltip, link, answer_type, answers, **kw):
        print "title: %s" % title
        print "category: %s" % category
        print "question: %s" % question
        print "tooltip: %s" % tooltip
        print "link: %s" % link
        print "answer_type: %s" % answer_type
        print "answers: %s" % answers

        if answer_type == "single" or answer_type == "multi":
            if len(answers) <= 0:
                response.status_code = 412
                return dict(
                    errors={'answers': 'Inserire almeno una risposta'})

        user = request.identity['user']

        model.Qa(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            question=question,
            tooltip=tooltip,
            type=answer_type,
            answers=answers,
            public=True,
            visible=True
        )
        return dict(errors=None)
