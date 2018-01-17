# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
import json

import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from ksweb.lib.utils import to_object_id
from tg import expose, validate, RestController, decode_params, request, \
    validation_errors_response,  response, tmpl_context, flash, lurl
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tg import require
from tg import session
from tw2.core import OneOfValidator, StringLengthValidator
from ksweb import model
from ksweb.lib.validator import QAExistValidator, CategoryExistValidator, PreconditionExistValidator


class PreconditionSimpleController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"


    @expose('ksweb.templates.precondition.simple.new')
    @validate({'workspace': CategoryExistValidator(required=True)})
    def new(self, workspace, **kw):
        return dict(page='precondition-new', workspace=workspace, qa_value=kw.get('qa_value'),
                    precondition={'question_content': kw.get('question_content', None),
                                  'question_title': kw.get('question_title', None)})
    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'question': QAExistValidator(required=True),
        'answer_type': OneOfValidator(values=[u'have_response', u'what_response'], required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, category, question, answer_type, interested_response, **kw):
        user = request.identity['user']

        qa = model.Qa.query.get(_id=ObjectId(question))

        #  CASO BASE in cui risco a creare un filtro semplice per definizione e' quella di che venga solamente selezionata una risposta
        if len(interested_response) == 1:
            #  La risposta e' solo una creo un filtro semplice
            created_precondition = model.Precondition(
                _owner=user._id,
                _category=ObjectId(category),
                title=title,
                type='simple',
                condition=[ObjectId(question), interested_response[0]]
            )
        else:
            #  CASO AVANZATO sono state selezionate piu' risposte, devo prima creare tutte i filtri semplici e poi creare quella complessa
            if answer_type == "have_response":
                #  Create one precondition simple for all possibility answer to question
                #  After that create a complex precondition with previous simple precondition
                interested_response = qa.answers

            if answer_type == "what_response":
                #  Create one precondition simple for all selected answer to question
                #  After that create a complex precondition with previous simple precondition

                if len(interested_response) <= 1:
                    response.status_code = 412
                    return dict(errors={'interested_response': _('Please select at least one answer')})

            base_precond = []
            for resp in interested_response:
                prec = model.Precondition(
                    _owner=user._id,
                    _category=ObjectId(category),
                    title="%s_%s" % (qa.title.upper(), resp.upper()),
                    type='simple',
                    condition=[ObjectId(question), resp],
                    public=True,
                    visible=False
                )
                base_precond.append(prec)

            condition = []
            for prc in base_precond[:-1]:
                condition.append(prc._id)
                condition.append('or')

            condition.append(base_precond[-1]._id)

            created_precondition = model.Precondition(
                _owner=user._id,
                _category=ObjectId(category),
                title=title,
                type='advanced',
                condition=condition
            )

        #flash(_("Now you can create an output <a href='%s'>HERE</a>" % lurl('/output?workspace='+ str(category))))

        return dict(precondition_id=str(created_precondition._id),errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': PreconditionExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'question': QAExistValidator(required=True),
        'answer_type': OneOfValidator(values=[u'what_response'], required=True),
    }, error_handler=validation_errors_response)
    @require(
        CanManageEntityOwner(
            msg=l_(u'You are not allowed to edit this filter.'),
            field='_id',
            entity_model=model.Precondition))
    def put(self, _id, title, category, question, answer_type, interested_response, **kw):

        check = self.get_related_entities(_id)
        if check.get("entities"):
            entity = dict(
                _id=_id,
                title=title,
                condition=[question, interested_response],
                _category=category,
                entity='precondition/simple'
            )
            session['entity'] = entity  # overwrite always same key for avoiding conflicts
            session.save()
            return dict(redirect_url=tg.url('/resolve', params=dict(workspace=category)))

        precondition = model.Precondition.query.get(_id=ObjectId(_id))
        precondition.title = title
        precondition.condition = [ObjectId(question), interested_response]
        precondition._category = category

        return dict(errors=None, redirect_url=None)

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        """
        This method return ALL entities (Output, Document) that have inside a `content.content` the given _id
        :param _id:
        :return:
        """

        # devo cercare nelle qa, nei filtri avanzati, negli output
        outputs_related = model.Output.query.find({'_precondition': ObjectId(_id)}).all()
        preconditions_related = model.Precondition.query.find({'type': 'advanced', 'condition': ObjectId(_id)}).all()
        qas_related = model.Qa.query.find({"_parent_precondition": ObjectId(_id)}).all()

        entities = list(outputs_related + preconditions_related + qas_related)

        return {
            'entities': entities,
            'len': len(entities)
        }

    @expose('ksweb.templates.precondition.simple.new')
    @validate({
        '_id': PreconditionExistValidator(),
        'workspace': CategoryExistValidator()
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this filter.'), field='_id', entity_model=model.Precondition))
    def edit(self, _id, workspace, **kw):
        precondition = model.Precondition.query.find({'_id': ObjectId(_id), '_category': ObjectId(workspace)}).first()
        return dict(precondition=precondition, workspace=workspace, errors=None)


    @expose('json')
    @decode_params('json')
    @validate({
        '_id': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id, **kw):
        precondition = model.Precondition.query.find({'_id': ObjectId(_id)}).first()
        return dict(precondition=precondition)
