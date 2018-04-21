# -*- coding: utf-8 -*-
"""Category controller module"""
from bson import ObjectId
from ksweb.model import Category, Qa, Output, Precondition, Document, Questionary
from tg import decode_params, predicates, request
from tg import expose, validate, RestController, validation_errors_response
from ksweb.lib.validator import WorkspaceExistValidator
from tg import flash
from tg import response
from tw2.core import StringLengthValidator
from tg.i18n import ugettext as _, lazy_ugettext as l_


class CategoryController(RestController):
    allow_only = predicates.has_any_permission('manage', 'lawyer', msg=l_('Only for admin or lawyer'))

    @expose('json')
    @validate({
        'id': WorkspaceExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def get_one(self, id, **kw):
        qa = Category.query.get(_id=ObjectId(id))
        return dict(qa=qa)

    @expose('json')
    def get_all(self):
        query = {'_owner': {'$in': [request.identity['user']._id, None]}, 'visible': True}
        categories = Category.query.find(query).sort('_id').all()
        return dict(categories=categories)

    @decode_params('json')
    @expose('json')
    @validate({
        'workspace_name': StringLengthValidator(min=2),
    }, error_handler=validation_errors_response)
    def create(self, workspace_name=None, **kw):
        user = request.identity['user']
        ws = Category.query.find({'name': workspace_name.encode('utf-8'), '_owner': user._id}).first()
        if ws:
            response.status_code = 412
            return dict(errors={'workspace_name': 'This category already exists'})

        workspace = Category(
            visible=True,
            name=workspace_name,
            _owner=user._id
        )

        flash(_(u"Workspace %s successfully created!" % workspace.name))
        return dict(workspaces=self.get_all())

    @decode_params('json')
    @expose('json')
    @validate({
        'workspace_id': WorkspaceExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def delete(self, method=None, workspace_id=None, **kw):
        workspace = Category.query.get(_id=ObjectId(workspace_id))
        if not workspace.owner:
            flash(_('This workspace can not be deleted'), 'warning')
            return dict(workspaces=self.get_all())
        Qa.query.remove({'_category': ObjectId(workspace_id)})
        Output.query.remove({'_category': ObjectId(workspace_id)})
        Precondition.query.remove({'_category': ObjectId(workspace_id)})
        documents = Document.query.find({'_category': ObjectId(workspace_id)}).all()
        doc = [document._id for document in documents]
        Questionary.query.remove({'_document': {'$in': doc}})
        Document.query.remove({'_id': {'$in': doc}})
        Category.query.remove({'_id': ObjectId(workspace_id)})
        flash(_("Category and all entities associated deleted"))
        return dict(workspaces=self.get_all())
