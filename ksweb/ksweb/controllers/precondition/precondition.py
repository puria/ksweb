# -*- coding: utf-8 -*-
"""Precondition controller module"""
from __future__ import print_function
import tg
from bson import ObjectId
from tg import request
from tg.decorators import paginate, decode_params, validate
from tg.i18n import lazy_ugettext as l_
from tg import expose, predicates, tmpl_context, validation_errors_response
from ksweb import model
from ksweb.lib.validator import PreconditionExistValidator, WorkspaceExistValidator
from ksweb.model import Precondition
from .simple import PreconditionSimpleController
from .advanced import PreconditionAdvancedController
from ksweb.lib.base import BaseController


class PreconditionController(BaseController):
    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))
    
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"
        
    simple = PreconditionSimpleController()
    advanced = PreconditionAdvancedController()

    @expose('ksweb.templates.precondition.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def index(self, workspace, **kw):
        return dict(
            page='precondition-index',
            fields={
                'columns_name': [l_('Label'), l_('Type'), l_('Owner')],
                'fields_name': ['title', 'type', 'owner']
            },
            entities=model.Precondition.precondition_available_for_user(request.identity['user']._id, workspace=workspace),
            actions_content=[l_('New Output'),l_('New Q/A')],
            workspace=workspace
        )

    @expose('json')
    def sidebar_precondition(self, workspace): #pragma: no cover
        res = list(model.Precondition.query.aggregate([
            {
                '$match': {
                    '_owner': request.identity['user']._id,
                    # 'visible': True
                    '_category': ObjectId(workspace)
                }
            },
            {
                '$group': {
                    '_id': '$_category',
                    'precondition': {'$push': "$$ROOT",}
                }
            }
        ]))

        #  Insert category name into res
        for e in res:
            e['category_name'] = model.Category.query.get(_id=ObjectId(e['_id'])).name

        return dict(precond=res)

    @expose('json')
    def available_preconditions(self, workspace=None):
        preconditions = Precondition.query.find({'_owner': request.identity['user']._id, 'visible': True, '_category': ObjectId(workspace)}).sort('title').all()
        return dict(preconditions=preconditions)

    @expose('json')
    @decode_params('json')
    @validate({
        'id': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def qa_precondition(self, id, **kw):
        precondition = model.Precondition.query.get(_id=ObjectId(id))
        return dict(qas=precondition.response_interested)

    @expose('json')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def mark_as_read(self, workspace, **kw):
        preconditions = Precondition.query.find({'_owner': request.identity['user']._id, 'visible': True, '_category': ObjectId(workspace)}).all()
        [p.mark_as_read(workspace) for p in preconditions]



