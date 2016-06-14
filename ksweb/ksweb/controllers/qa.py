# -*- coding: utf-8 -*-
"""Qa controller module"""
from bson import ObjectId
from tg import expose, validate, validation_errors_response, response, RestController, decode_params, request, tmpl_context
import tg
from tg.decorators import paginate
from tg.i18n import lazy_ugettext as l_
from tg import predicates
from tw2.core import StringLengthValidator, OneOfValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, QAExistValidator


class QaController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "qas"

    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.qa.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    def get_all(self, **kw):
        return dict(
            page='qa-index',
            fields={
                'columns_name': ['Name', 'Category', 'Question', 'Type'],
                'fields_name': ['title', 'category', 'question', 'type']
            },
            entities=model.Qa.query.find().sort('title'),
            actions=True
        )

    @expose('json')
    @validate({
        'id': QAExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def get_one(self, id,  **kw):
        qa = model.Qa.query.get(_id=ObjectId(id))
        return dict(qa=qa)

    @expose('json')
    def get_single_or_multi_question(self):
        questions = model.Qa.query.find({'type': {'$in': ['single', 'multi']}, 'public': True}).all()
        return dict(questions=[{'_id': qa._id, 'title': qa.title} for qa in questions])

    @expose('json')
    @expose('ksweb.templates.qa.new')
    def new(self, **kw):
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'question': StringLengthValidator(min=2),
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

        qa = model.Qa(
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

        if answer_type == 'text':  # model.Qa.QA_TYPE[0]
                        model.Precondition(
                            _owner=user._id,
                            _category=ObjectId(category),
                            title=title + ' compilata',
                            type='simple',
                            condition=[qa._id, ''])

        return dict(errors=None)
