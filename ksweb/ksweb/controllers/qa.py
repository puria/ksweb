# -*- coding: utf-8 -*-
"""Qa controller module"""
import json

from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from ksweb.lib.utils import to_object_id
from tg import expose, validate, validation_errors_response, response, RestController, \
    decode_params, request, tmpl_context, session, flash, lurl
import tg
from tg.decorators import paginate, require
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import predicates
from tw2.core import StringLengthValidator, OneOfValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, QAExistValidator, PreconditionExistValidator


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
                'columns_name': [_('Label'), _('Question'), _('Filter'), _('Category')],
                'fields_name': ['title', 'question', 'parent_precondition', 'category']
            },
            entities=model.Qa.qa_available_for_user(request.identity['user']._id),
            actions=False
        )

    @expose('json')
    @validate({
        'id': QAExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def get_one(self, id,  **kw):
        qa = model.Qa.query.find({'_id': ObjectId(id), '_owner': request.identity['user']._id}).first()
        return dict(qa=qa)

    @expose('json')
    def get_single_or_multi_question(self):
        questions = model.Qa.query.find({
            'type': {'$in': ['single', 'multi']},
            '_owner': request.identity['user']._id
        }).all()
        return dict(questions=[{'_id': qa._id, 'title': qa.title} for qa in questions])

    @expose('json')
    @expose('ksweb.templates.qa.new')
    def new(self, **kw):
        return dict(errors=None, qa={})

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'question': StringLengthValidator(min=2),
        'tooltip': StringLengthValidator(min=0, max=100),
        'link': StringLengthValidator(min=0, max=100),
        'answer_type': OneOfValidator(values=model.Qa.QA_TYPE, required=True),
        'precondition': PreconditionExistValidator(required=False),
    }, error_handler=validation_errors_response)
    def post(self, title, category, question, tooltip, link, answer_type, precondition=None, answers=None, **kw):

        if answer_type == "single" or answer_type == "multi":
            if len(answers) < 2:
                response.status_code = 412
                return dict(
                    errors={'answers': _('Please add at least one more answer')})

        user = request.identity['user']

        qa = model.Qa(
                _owner=user._id,
                _category=ObjectId(category),
                _parent_precondition=ObjectId(precondition) if precondition else None,
                title=title,
                question=question,
                tooltip=tooltip,
                link=link,
                type=answer_type,
                answers=answers,
                public=True,
                visible=True
            )

        if answer_type == 'text':   # model.Qa.QA_TYPE[0]
                        model.Precondition(
                            _owner=user._id,
                            _category=ObjectId(category),
                            title=title + ' compilata',
                            type='simple',
                            condition=[qa._id, ''])

        if qa.is_text:
            flash(_("Now you can create an output <a href='%s'>HERE</a>" % lurl('/output')))
        else:
            flash(_("Now you can create a simple filter or an advanced one <a href='%s'>HERE</a> " % lurl('/precondition')))

        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': QAExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'question': StringLengthValidator(min=2),
        'tooltip': StringLengthValidator(min=0, max=100),
        'link': StringLengthValidator(min=0, max=100),
        'answer_type': OneOfValidator(values=model.Qa.QA_TYPE, required=True),
        'precondition': PreconditionExistValidator(required=False),
    }, error_handler=validation_errors_response)
    def put(self, _id, title, category, question, tooltip, link, answer_type, precondition=None, answers=None, **kw):

        if answer_type == "single" or answer_type == "multi":
            if len(answers) < 2:
                response.status_code = 412
                return dict(
                    errors={'answers': _('Please add at least one more answer')})

        user = request.identity['user']

        check = self.get_related_entities(_id)
        if check.get("entities"):
            entity = dict(
                _id=_id,
                title=title,
                _category=category,
                entity='qa',
                question=question,
                tooltip=tooltip,
                link=link,
                type=answer_type,
                _parent_precondition=precondition,
                answers=answers
            )
            session['entity'] = entity  # overwrite always same key for avoiding conflicts
            session.save()
            return dict(redirect_url=tg.url('/resolve'))

        qa = model.Qa.query.get(_id=ObjectId(_id))
        qa._category = ObjectId(category)
        qa._parent_precondition = to_object_id(precondition)
        qa.title = title
        qa.question = question
        qa.tooltip = tooltip
        qa.question = question
        qa.link = link
        qa.type = answer_type
        qa.answers = answers

        if answer_type == 'text':   # model.Qa.QA_TYPE[0]
                        model.Precondition(
                            _owner=user._id,
                            _category=ObjectId(category),
                            title=title + ' compilata',
                            type='simple',
                            condition=[qa._id, ''])

        return dict(errors=None)

    @expose('ksweb.templates.qa.new')
    @validate({
        '_id': QAExistValidator(model=True)
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You can not edit this Q/A'), field='_id', entity_model=model.Qa))
    def edit(self, _id, **kw):
        qa = model.Qa.query.find({'_id': ObjectId(_id)}).first()
        return dict(qa=qa, errors=None)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': QAExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id, **kw):
        qa = model.Qa.query.find({'_id': ObjectId(_id)}).first()
        return dict(qa=qa)

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        """
        This method return ALL entities (Precondition simple) that have inside the given _id
        :param _id:
        :return:
        """
        preconditions_related = model.Precondition.query.find({'type': 'simple', 'condition': ObjectId(_id)})
        entities = list(preconditions_related)
        return {
            'entities': entities,
            'len': len(entities)
        }