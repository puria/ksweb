# -*- coding: utf-8 -*-
"""Precondition controller module"""
from __future__ import print_function
import tg
from bson import ObjectId
from tg import request, redirect
from tg.decorators import paginate, decode_params, validate
from tg.i18n import lazy_ugettext as l_
from tg import expose, predicates, tmpl_context, validation_errors_response
from ksweb.lib.validator import PreconditionExistValidator, WorkspaceExistValidator
from ksweb.model import Precondition, Workspace
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
                'columns_name': [l_('Label'), l_('Type'), l_('Owner'), l_('Id')],
                'fields_name': 'title type owner hash'.split()
            },
            entities=Precondition.available_for_user(request.identity['user']._id, workspace=workspace),
            actions_content=[l_('New Output'),l_('New QA')],
            workspace=workspace
        )

    @expose('json')
    def sidebar_precondition(self, workspace):  # pragma: no cover
        res = list(Precondition.query.aggregate([
            {
                '$match': {
                    '_owner': request.identity['user']._id,
                    '_workspace': ObjectId(workspace)
                }
            },
            {
                '$group': {
                    '_id': '$_workspace',
                    'precondition': {'$push': "$$ROOT", }
                }
            }
        ]))

        #  Insert workspace name into res
        for e in res:
            e['workspace_name'] = Workspace.query.get(_id=ObjectId(e['_id'])).name

        return dict(precond=res)

    @expose('json')
    def available_preconditions(self, workspace=None):
        preconditions = Precondition.available_for_user(request.identity['user']._id, workspace=workspace).all()
        return dict(preconditions=preconditions)

    @expose('json')
    @decode_params('json')
    @validate({
        'id': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def qa_precondition(self, id, **kw):
        precondition = Precondition.query.get(_id=ObjectId(id))
        return dict(qas=precondition.response_interested)

    @expose('json')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def mark_as_read(self, workspace):
        Precondition.mark_as_read(request.identity['user']._id, workspace)

    @expose('json')
    def open(self, _id):
        if not _id:
            tg.flash('The precondition you are looking for, does not exist')
            redirect()
        p = Precondition.query.get(_id=ObjectId(_id))
        redirect('/%s/edit' % (p.entity), params=dict(_id=p._id, workspace=p._workspace))

