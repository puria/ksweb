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
from ksweb.model import Category, Output, Precondition, Qa
from ksweb.lib.validator import WorkspaceExistValidator, QAExistValidator, PreconditionExistValidator


class QaController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "qas"

    allow_only = predicates.not_anonymous(msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.qa.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': WorkspaceExistValidator(required=True), },
              error_handler=validation_errors_response)
    def get_all(self, workspace=None, **kw):
        return dict(
            page='qa-index',
            fields={
                'columns_name': [_('Label'), _('Question'), _('Filter')],
                'fields_name': ['title', 'question', 'parent_precondition']
            },
            entities=Qa.qa_available_for_user(request.identity['user']._id, workspace),
            actions=False,
            workspace=workspace
        )

    @expose('json')
    @validate({
        'id': QAExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def get_one(self, id,  **kw):
        qa = Qa.query.find({'_id': ObjectId(id)}).first()
        return dict(qa=qa)

    @expose('json')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def get_single_or_multi_question(self, workspace):
        questions = Qa.query.find({
            'type': {'$in': ['single', 'multi']},
            '_owner': request.identity['user']._id,
            '_category': ObjectId(workspace)
        }).all()
        return dict(questions=[{'_id': qa._id, 'title': qa.title} for qa in questions])

    @expose('json')
    @expose('ksweb.templates.qa.new')
    @validate({'workspace': WorkspaceExistValidator(required=True), })
    def new(self, workspace, **kw):
        return dict(errors=None, workspace=workspace, referrer=kw.get('referrer'),
                    qa={'question': kw.get('question_content', None),
                        'title': kw.get('question_title', None),
                        '_parent_precondition': kw.get('precondition_id', None)})

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': WorkspaceExistValidator(required=True),
        'question': StringLengthValidator(min=2),
        'tooltip': StringLengthValidator(min=0, max=100),
        'link': StringLengthValidator(min=0, max=100),
        'answer_type': OneOfValidator(values=Qa.QA_TYPE, required=True),
        'precondition': PreconditionExistValidator(required=False),
    }, error_handler=validation_errors_response)
    def post(self, title, category, question, tooltip, link, answer_type, precondition=None, answers=None, **kw):
        if not self._are_answers_valid(answer_type, answers):
            response.status_code = 412
            return dict(errors={'answers': _('Please add at least one more answer')})

        user = request.identity['user']

        qa = Qa(
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

        self._autofill_qa_filters(qa)
        return dict(errors=None, _id=ObjectId(qa._id))

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': QAExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': WorkspaceExistValidator(required=True),
        'question': StringLengthValidator(min=2),
        'tooltip': StringLengthValidator(min=0, max=100),
        'link': StringLengthValidator(min=0, max=100),
        'answer_type': OneOfValidator(values=Qa.QA_TYPE, required=True),
        'precondition': PreconditionExistValidator(required=False),
    }, error_handler=validation_errors_response)
    def put(self, _id, title, category, question, tooltip, link, answer_type,
                  precondition=None, answers=None, **kw):
        if not self._are_answers_valid(answer_type, answers):
            response.status_code = 412
            return dict(errors={'answers': _('Please add at least one more answer')})

        check = self.get_related_entities(_id)

        if check.get("entities"):
            entity = dict(
                _id=_id, _category=category,
                title=title, entity='qa',
                question=question,
                tooltip=tooltip, link=link,
                type=answer_type,
                _parent_precondition=precondition,
                answers=answers
            )

            session.data_serializer = 'pickle'
            session['entity'] = entity  # overwrite always same key for avoiding conflicts
            session.save()

            return dict(redirect_url=tg.url('/resolve', params=dict(workspace=category)))

        qa = Qa.query.get(_id=ObjectId(_id))
        qa._category = ObjectId(category)
        qa._parent_precondition = to_object_id(precondition)
        qa.title = title
        qa.question = question
        qa.tooltip = tooltip
        qa.question = question
        qa.link = link
        qa.type = answer_type
        qa.answers = answers
        self._autofill_qa_filters(qa)

        return dict(errors=None)

    @expose('ksweb.templates.qa.new')
    @validate({
        '_id': QAExistValidator(model=True)
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You can not edit this Q/A'), field='_id', entity_model=Qa))
    def edit(self, _id, workspace=None, **kw):
        ws = Category.query.find({'_id': ObjectId(workspace)}).first()
        if not ws:
            return tg.abort(404)
        qa = Qa.query.find({'_id': ObjectId(_id)}).first()
        return dict(qa=qa, workspace=ws._id, errors=None)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': QAExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id, **kw):
        qa = Qa.query.find({'_id': ObjectId(_id)}).first()
        return dict(qa=qa)

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        """
        This method return ALL entities (Precondition simple) that have inside the given _id
        :param _id:
        :return:
        """

        preconditions_related = Precondition.query.find({'type': 'simple', 'condition': ObjectId(_id)})
        entities = list(preconditions_related)
        return {
            'entities': entities,
            'len': len(entities)
        }

    def _autofill_qa_filters(self, qa):
        user = request.identity['user']
        if qa.type == 'text':   # Qa.QA_TYPE[0]
            autogen_filter = Precondition(
                                _owner=user._id,
                                _category=ObjectId(qa._category),
                                title=qa.title + _(u' \u21d2 was compiled'),
                                type='simple',
                                auto_generated=True,
                                status=Precondition.STATUS.UNREAD,
                                condition=[qa._id, ''])
        else:
            base_precond = []
            for answer in qa.answers:
                prec = Precondition(
                    _owner=user._id,
                    _category=ObjectId(qa._category),
                    title=qa.title + u' \u21d2 %s' % answer,
                    type='simple',
                    auto_generated=True,
                    status=Precondition.STATUS.UNREAD,
                    condition=[qa._id, answer],
                )
                base_precond.append(prec)

            condition = []
            for prc in base_precond[:-1]:
                condition.append(prc._id)
                condition.append('or')

            condition.append(base_precond[-1]._id)

            autogen_filter = Precondition(
                _owner=user._id,
                _category=ObjectId(qa._category),
                title=qa.title + _(u' \u21d2 was compiled'),
                type='advanced',
                auto_generated=True,
                status=Precondition.STATUS.UNREAD,
                condition=condition
            )

        if autogen_filter:
            Output(
                _owner=user._id,
                _category=ObjectId(qa._category),
                _precondition=ObjectId(autogen_filter._id),
                title=qa.title + u' \u21d2 output',
                auto_generated=True,
                html='${qa_%s}' % qa._id,
                status=Precondition.STATUS.UNREAD,
                content= [dict(content=str(qa._id), type='qa_response', title=qa.title)]
            )

    def _are_answers_valid(self, answer_type, answers):
        if (answer_type == "single" and len(answers) < 2) or\
           (answer_type == "multi" and len(answers) < 1):
            return False
        return True
