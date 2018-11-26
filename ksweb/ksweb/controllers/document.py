# -*- coding: utf-8 -*-
"""Document controller module"""
import json

import tg
from bson import ObjectId
from ksweb.lib.importers.json_importer import JsonImporter
from tg.renderers import json as json_render
from tgext.datahelpers.utils import slugify

from ksweb.lib.predicates import CanManageEntityOwner
from tg import expose, tmpl_context, predicates, RestController, request, validate, \
    validation_errors_response, flash
from tg import redirect
from tg import response
from tg.decorators import paginate, decode_params, require
from tg.i18n import lazy_ugettext as l_, ugettext as _
from tw2.core import StringLengthValidator
from ksweb import model
from ksweb.lib.validator import WorkspaceExistValidator, DocumentExistValidator,\
    DocumentContentValidator


class DocumentController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "documents"

    allow_only = predicates.has_any_permission('manage', 'lawyer',
                                               msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.document.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def get_all(self, workspace, **kw):
        return dict(
            page='document-index',
            fields={
                'columns_name': [_('Title'), _('Description'), _('Version'), _('License')],
                'fields_name': ['title', 'description', 'version', 'license']
            },
            entities=model.Document.document_available_for_user(request.identity['user']._id, workspace=workspace),
            actions_content=[_('Export'), _('Create Form')],
            workspace=workspace,
            download=True
        )

    @expose('ksweb.templates.document.new')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def new(self, workspace, **kw):
        tmpl_context.sidebar_document = "document-new"
        return dict(document={}, workspace=workspace, errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'workspace': WorkspaceExistValidator(required=True),
        'html': DocumentContentValidator(strip=False),
        'description': StringLengthValidator(min=0),
        'license': StringLengthValidator(min=0, max=100),
        'version': StringLengthValidator(min=0, max=100),
        'tags': StringLengthValidator(min=0, max=100)
    }, error_handler=validation_errors_response)
    def post(self, title, workspace, description, license, version, tags, html, **kw):
        user = request.identity['user']
        tags = {__.strip() for __ in tags.split(',')} if tags else []

        doc = model.Document(
            _owner=user._id,
            _category=ObjectId(workspace),
            title=title,
            public=True,
            visible=True,
            html=html,
            description=description,
            license=license,
            version=version,
            tags=list(tags)
        )
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': DocumentExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'workspace': WorkspaceExistValidator(required=True),
        'html': DocumentContentValidator(strip=False),
        'description': StringLengthValidator(min=0),
        'license': StringLengthValidator(min=0, max=100),
        'version': StringLengthValidator(min=0, max=100),
        'tags': StringLengthValidator(min=0),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'),
                                  field='_id',
                                  entity_model=model.Document))
    def put(self, _id, title, html, workspace, description, license, version, tags, **kw):
        tags = {__.strip() for __ in tags.split(',')} if tags else []
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()
        document.title = title
        document._category = ObjectId(workspace)
        document.html = html
        document.tags = list(tags)
        document.description = description
        document.license = license
        document.version = version
        return dict(errors=None)

    @expose('ksweb.templates.document.new')
    @validate({
        '_id': DocumentExistValidator(required=True),
        'workspace': WorkspaceExistValidator(required=True)
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'),
                                  field='_id',
                                  entity_model=model.Document))
    def edit(self, _id, workspace, **kw):
        tmpl_context.sidebar_document = "document-new"
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()
        return dict(document=document, workspace=workspace, errors=None)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': DocumentExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id, **kw):
        # TODO: implement something meaningful
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()
        return dict(document=document)

    @expose("json", content_type='application/json')
    @validate({
        '_id': DocumentExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def export(self, _id):
        document = model.Document.query.get(_id=ObjectId(_id))
        filename = slugify(document, document.title)
        response.headerlist.append(('Content-Disposition', str('attachment;filename=%s.json' % filename)))
        encoded = json_render.encode(document.export())
        return json.dumps(json.loads(encoded), sort_keys=True, indent=4)

    @expose()
    @validate({
        'workspace': WorkspaceExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def import_document(self, workspace, file_import):
        owner = request.identity['user']._id
        file_content = file_import.file.read()
        importer = JsonImporter(file_content, ObjectId(workspace), owner)
        importer.run()
        tg.flash(_('Document successfully imported!'))
        return redirect(tg.url('/document', params=dict(workspace=workspace)))
