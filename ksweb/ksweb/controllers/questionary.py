# -*- coding: utf-8 -*-
"""Questionary controller module"""
from string import Template

from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from markupsafe import Markup
from tg import expose, response, validate, flash, url, predicates, validation_errors_response, decode_params, request, \
    tmpl_context
from tg import redirect
from tg.decorators import paginate, require
from tg.i18n import lazy_ugettext as l_
import tg
from tg.i18n import ugettext as _
from tw2.core import StringLengthValidator

from ksweb import model
from ksweb.lib.base import BaseController
from ksweb.lib.validator import QuestionaryExistValidator, DocumentExistValidator, QAExistValidator, \
    CategoryExistValidator
from ksweb.model import DBSession
try:
    basestring
except NameError:
    basestring = str


class QuestionaryController(BaseController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "questionaries"

    allow_only = predicates.has_any_permission('manage', 'lawyer', msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.questionary.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': CategoryExistValidator(required=True)})
    def index(self, workspace, **kw):
        user = request.identity['user']
        documents_id = [ObjectId(documents._id) for documents in
                        model.Document.document_available_for_user(user_id=user._id, workspace=workspace).all()]
        entities = model.Questionary.query.find({'$or': [
            {'_user': ObjectId(user._id)},
            {'_owner': ObjectId(user._id)}
        ], '_document': {'$in': documents_id}}).sort('title')
        return dict(
            page='questionary-index',
            fields={
                'columns_name': [_('Title'), _('Owner'), _('Shared with'), _('Created on'), _('Completion %')],
                'fields_name': ['title', '_owner', '_user', 'creation_date', 'completion']
            },
            entities=entities,
            actions=False,
            actions_content=['Esporta'],
            workspace=workspace
        )

    @decode_params('json')
    @expose('json')
    @validate({
        'questionary_title': StringLengthValidator(min=2),
        'document_id': DocumentExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def create(self, questionary_title=None, document_id=None, **kw):
        #  create questionary for himself
        user = request.identity['user']
        questionary = model.Questionary(
            title=questionary_title,
            _user=user._id,
            _owner=user._id,
            _document=ObjectId(document_id),
        )
        return dict(questionary=questionary)

    @expose('ksweb.templates.questionary.compile')
    @expose('json')
    @validate({
        '_id': QuestionaryExistValidator(required=True),
        'workspace': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this questionary.'), field='_id',
                                  entity_model=model.Questionary))
    def compile(self, _id, workspace, **kwargs):
        questionary = model.Questionary.query.get(_id=ObjectId(_id))
        return dict(questionary=questionary, quest_compiled=questionary.evaluate_questionary,
                    html=self.get_questionary_html(_id), workspace=workspace)

    @expose('odt:ksweb.templates.questionary.questionary', content_type='application/vnd.oasis.opendocument.text')
    @validate({
        '_id': QuestionaryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this questionary.'), field='_id',
                                  entity_model=model.Questionary))
    def download(self, _id):
        questionary = model.Questionary.query.get(_id=ObjectId(_id))
        response.headerlist.append(('Content-Disposition',
                                    'attachment;filename=%s.odt' % questionary.title))
        return dict(content=self.get_questionary_html(_id).striptags())

    @staticmethod
    def get_questionary_html(quest_id):
        questionary = model.Questionary.query.get(_id=ObjectId(quest_id))
        questionary_compiled = Template(questionary.document.html)

        output_values, qa_values = dict(), dict()

        for output_dict in questionary.document.content:
            _id = ObjectId(output_dict['content'])
            if output_dict['content'] in questionary.output_values and \
                    questionary.output_values[output_dict['content']]['evaluation']:
                output = model.Output.query.get(_id=_id)
                output_values['output_' + str(_id)] = output.render(questionary.output_values)
            else:
                # this clear useless output placeholder
                output_values['output_' + str(_id)] = ''
        questionary_compiled = questionary_compiled.safe_substitute(**output_values)
        questionary_compiled = Template(questionary_compiled)

        for qa_id, resp in questionary.qa_values.items():
            qa_values['qa_' + qa_id] = Markup.escape(resp['qa_response'])

        return Markup(questionary_compiled.safe_substitute(**qa_values))

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': QuestionaryExistValidator(required=True),
        'qa_id': QAExistValidator(required=True),
        'qa_response': StringLengthValidator(min=1, strip=False),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this questionary.'), field='_id',
                                  entity_model=model.Questionary))
    def responde(self, _id=None, qa_id=None, qa_response=None, **kwargs):
        questionary = model.Questionary.query.get(_id=ObjectId(_id))
        #  Check if the qa response is valid
        qa = model.Qa.query.get(_id=ObjectId(qa_id))
        if qa.type == "single" and not qa_response in qa.answers:
            response.status_code = 412
            return dict(errors={'qa_response': _('Invalid answer')})

        if qa.type == "multi":
            #  check each qa_response if is in qa.answers
            if isinstance(qa_response, basestring):
                qa_response = [qa_response]

                # This comment is needed for to allow users to 'not response' a question
                # For disable this, just uncomment followings rows

                # for elem in qa_response:
                #     if not elem in qa.answers:
                #         response.status_code = 412
                #         return dict(errors={'qa_response': _('Invalid answer')})

        if not questionary.qa_values:
            order_number = 0
        else:
            order_number = max([questionary.qa_values[elem]['order_number'] for elem in questionary.qa_values]) + 1
        questionary.qa_values[qa_id] = {'qa_response': qa_response, 'order_number': order_number}

        # Not sure about flush here
        DBSession.flush(questionary)
        quest_compiled = questionary.evaluate_questionary

        return dict(questionary=questionary, quest_compiled=quest_compiled, html=self.get_questionary_html(_id))

    @expose('ksweb.templates.questionary.completed')
    @validate({
        '_id': QuestionaryExistValidator(required=True),
        'workspace': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def completed(self, _id=None, workspace=None):
        questionary = model.Questionary.query.get(_id=ObjectId(_id))
        completed = questionary.evaluate_questionary
        if not completed:
            return redirect('/questionary/compile', params=dict(quest_complited=completed, workspace=workspace))

        questionary_compiled = Template(questionary.document.html)
        output_values, qa_values = dict(), dict()

        for output_dict in questionary.document.content:
            _id = ObjectId(output_dict['content'])
            if questionary.output_values[output_dict['content']]:
                output = model.Output.query.get(_id=_id)
                output_values['output_' + str(_id)] = output.render(questionary.output_values)
            else:
                # this clear useless output placeholder
                output_values['output_' + str(_id)] = ''

        questionary_compiled = questionary_compiled.safe_substitute(**output_values)
        questionary_compiled = Template(questionary_compiled)

        for qa_id, resp in questionary.qa_values.items():
            qa_values['qa_' + qa_id] = Markup.escape(resp['qa_response'])

        questionary_compiled = questionary_compiled.safe_substitute(**qa_values)

        return dict(questionary_compiled=Markup(questionary_compiled), workspace=workspace)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': QuestionaryExistValidator(required=True)
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this questionary.'), field='_id',
                                  entity_model=model.Questionary))
    def previous_question(self, _id=None, **kwargs):
        questionary = model.Questionary.query.get(_id=ObjectId(_id))

        if questionary.qa_values:
            last_order_number = max([questionary.qa_values[qa_val]['order_number'] for qa_val in questionary.qa_values])
            last_question_answered = [qa_val for qa_val in questionary.qa_values
                                      if questionary.qa_values[qa_val]['order_number'] == last_order_number][0]
            previous_response = questionary.qa_values[last_question_answered]['qa_response']
            questionary.qa_values.pop(last_question_answered, None)
            DBSession.flush_all()

        return dict(questionary=questionary,
                    quest_compiled=questionary.evaluate_questionary,
                    html=self.get_questionary_html(_id),
                    previous_response=previous_response)
