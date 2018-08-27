# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""

import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from ksweb.lib.utils import get_related_entities_for_filters
from ksweb.model import Qa, Precondition
from tg import expose, validate, RestController, decode_params, request, \
    validation_errors_response,  response, tmpl_context
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import require
from tg import session
from tw2.core import OneOfValidator, StringLengthValidator
from ksweb.lib.validator import QAExistValidator, WorkspaceExistValidator, PreconditionExistValidator


class PreconditionSimpleController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"

    @expose()
    def get_all(self, workspace, **kw):
        tg.redirect('/precondition', params=dict(workspace=workspace))

    @expose('ksweb.templates.precondition.simple.new')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def new(self, workspace, **kw):
        return dict(page='precondition-new', workspace=workspace, qa_value=kw.get('qa_value'),
                    precondition={'question_content': kw.get('question_content', None),
                                  'question_title': kw.get('question_title', None)})

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'workspace': WorkspaceExistValidator(required=True),
        'question': QAExistValidator(required=True),
        'answer_type': OneOfValidator(values=[u'have_response', u'what_response']),
    }, error_handler=validation_errors_response)
    def post(self, title, workspace, question, answer_type, interested_response=[], **kw):
        user = request.identity['user']
        qa = Qa.query.get(_id=ObjectId(question))
        _type = Precondition.TYPES.SIMPLE

        if qa.is_text:
            _condition = [ObjectId(question), '']
        else:
            if answer_type == 'have_response':
                interested_response = qa.answers
            answers_len = len(interested_response)
            if answers_len < 1:
                response.status_code = 412
                return dict(errors={'interested_response': _('Please select at least one answer')})

            if answers_len == 1:
                _condition = [ObjectId(question), interested_response[0]]
            else:
                advanced_condition = []
                for answer in interested_response:
                    ___ = Precondition(
                        _owner=user._id,
                        _category=ObjectId(workspace),
                        title="%s_%s" % (qa.title.upper(), answer.upper()),
                        type=_type,
                        condition=[qa._id, answer],
                        public=True,
                        visible=False
                    )
                    advanced_condition.append(___._id)
                    advanced_condition.append('or')
                del advanced_condition[-1]

                _condition = advanced_condition
                _type = Precondition.TYPES.ADVANCED

        new_filter = Precondition(
            _owner=user._id,
            _category=ObjectId(workspace),
            title=title,
            type=_type,
            condition=_condition
        )


        return dict(precondition_id=str(new_filter._id), errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': PreconditionExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': WorkspaceExistValidator(required=True),
        'question': QAExistValidator(required=True),
        'answer_type': OneOfValidator(values=[u'what_response'], required=True),
    }, error_handler=validation_errors_response)
    @require(
        CanManageEntityOwner(
            msg=l_(u'You are not allowed to edit this filter.'),
            field='_id',
            entity_model=Precondition))
    def put(self, _id, title, category, question, interested_response, **kw):
        check = self.get_related_entities(_id)
        if check.get("entities"):
            entity = dict(
                _id=_id,
                title=title,
                condition=[question, interested_response],
                _category=category,
                auto_generated=False,
                entity='precondition/simple'
            )
            session['entity'] = entity  # overwrite always same key for avoiding conflicts
            session.save()
            return dict(redirect_url=tg.url('/resolve', params=dict(workspace=category)))

        precondition = Precondition.query.get(_id=ObjectId(_id))
        precondition.title = title
        precondition.condition = [ObjectId(question), interested_response]
        precondition._category = category

        return dict(errors=None, redirect_url=None)

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        return get_related_entities_for_filters(_id)

    @expose('ksweb.templates.precondition.simple.new')
    @validate({
        '_id': PreconditionExistValidator(),
        'workspace': WorkspaceExistValidator()
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this filter.'), field='_id', entity_model=Precondition))
    def edit(self, _id, workspace):
        precondition = Precondition.query.find({'_id': ObjectId(_id), '_category': ObjectId(workspace)}).first()
        return dict(precondition=precondition, workspace=workspace, errors=None)


    @expose('json')
    @decode_params('json')
    @validate({
        '_id': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id):
        precondition = Precondition.query.find({'_id': ObjectId(_id)}).first()
        return dict(precondition=precondition)
