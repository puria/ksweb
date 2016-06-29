# -*- coding: utf-8 -*-
"""Questionary controller module"""
from bson import ObjectId
from tg import expose, response, validate, flash, url, predicates, validation_errors_response, decode_params, request, \
    tmpl_context
from tg.decorators import paginate
from tg.i18n import lazy_ugettext as l_
import tg
# from tg.i18n import ugettext as _
from tw2.core import StringLengthValidator

from ksweb import model
from ksweb.lib.base import BaseController
from ksweb.lib.validator import DocumentExistValidator


class QuestionaryController(BaseController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "questionaries"

    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))
    
    @expose('ksweb.templates.questionary.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    def index(self, **kw):
        user = request.identity['user']

        return dict(
            page='questionary-index',
            fields={
                'columns_name': ['Nome'],
                'fields_name': ['title']
            },
            entities=model.Questionary.query.find({'$or': [
                    {'_user': ObjectId(user._id)},
                    {'_owner': ObjectId(user._id)}
                ]}).sort('title'),
            actions=True
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
        model.Questionary(
            title=questionary_title,
            _user=user._id,
            _owner=user._id,
            _document=ObjectId(document_id),
        )
        return dict()
