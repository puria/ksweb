# -*- coding: utf-8 -*-
"""Document controller module"""
import json
from string import Template

import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from ksweb.lib.utils import import_output, export_outputs
from tg import expose, tmpl_context, predicates, RestController, request, validate, validation_errors_response
from tg import redirect
from tg import response
from tg.decorators import paginate, decode_params, require
from tg.i18n import lazy_ugettext as l_, ugettext as _
from tw2.core import StringLengthValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, DocumentExistValidator, DocumentContentValidator
from ksweb.lib.forms import UploadFileForm


class DocumentController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "documents"

    allow_only = predicates.has_any_permission('manage', 'lawyer', msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.document.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': CategoryExistValidator(required=True)})
    def get_all(self, workspace, **kw):
        return dict(
            page='document-index',
            fields={
                'columns_name': [_('Title'), _('Description'),_('Version'), _('License')],
                'fields_name': ['title', 'description', 'version', 'licence']
            },
            entities=model.Document.document_available_for_user(request.identity['user']._id, workspace=workspace),
            actions_content=[_('Export'), _('Create Questionary')],
            workspace=workspace,
            download=True
        )

    @expose('ksweb.templates.document.new')
    @validate({'workspace': CategoryExistValidator(required=True)})
    def new(self, workspace, **kw):
        tmpl_context.sidebar_document = "document-new"
        return dict(document={}, workspace=workspace, errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'content': DocumentContentValidator(),
        'description': StringLengthValidator(min=0),
        'licence': StringLengthValidator(min=0, max=100),
        'version': StringLengthValidator(min=0, max=100),
        'tags': StringLengthValidator(min=0, max=100)
    }, error_handler=validation_errors_response)
    def post(self, title, category, description, licence, version, tags, content=[],   **kw):

        if not content:
            content = []

        user = request.identity['user']

        tags = tags.strip().split(',') if tags else []

        model.Document(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            content=content,
            public=True,
            visible=True,
            html=kw['ks_editor'],
            description=description,
            licence=licence,
            version=version,
            tags=tags
        )
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': DocumentExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'content': DocumentContentValidator(),
        'description': StringLengthValidator(min=0),
        'licence': StringLengthValidator(min=0, max=100),
        'version': StringLengthValidator(min=0, max=100),
        'tags': StringLengthValidator(min=0),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'), field='_id',
                                  entity_model=model.Document))
    def put(self, _id, title, content, category, description, licence, version, tags, **kw):

        if not content:
            content = []
        tags = tags.strip().split(',') if tags else []
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()

        document.title = title
        document._category = ObjectId(category)
        document.content = content
        document.html = kw['ks_editor']
        document.tags = tags
        document.description = description
        document.licence = licence
        document.version = version

        return dict(errors=None)

    @expose('ksweb.templates.document.new')
    @validate({
        '_id': DocumentExistValidator(required=True),
        'workspace': CategoryExistValidator(required=True)
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'), field='_id',
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
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()
        return dict(document=document)

    @expose("json", content_type='application/json')
    @validate({
        '_id': DocumentExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def export(self, _id):
        document = model.Document.query.get(_id=ObjectId(_id)).__json__()
        response.headerlist.append(('Content-Disposition', str('attachment;filename=%s.json' % _id)))
        document.pop('_category', None)
        document.pop('_id', None)
        document.pop('entity', None)
        document['outputs'],  document['advanced_preconditions'], document['simple_preconditions'], document['qa'] = \
            dict(), dict(), dict(), dict()
        for output in document['content']:
            export_outputs(output['content'], document)
        return document

    @expose()
    @validate({
        'workspace': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def import_document(self, workspace, file_import):
        imported_document = json.load(file_import.file)
        content = []
        values = {}
        for output in imported_document['content']:
            c = {'type': output['type'], 'title': output['title'], 'content': str(
                import_output(imported_document, str(output['content']), imported_document['_owner'], workspace))}
            content.append(c)
            values['output_' + output['content']] = '${output_' + c['content'] + '}'
        html = Template(imported_document['html']).safe_substitute(**values)
        model.Document(
            _owner=imported_document['_owner'],
            _category=ObjectId(workspace),
            title=imported_document['title'],
            content=content,
            public=imported_document['public'],
            visible=imported_document['visible'],
            html=html,
            version=imported_document['version'],
            description=imported_document['description'],
            licence=imported_document['licence'],
            tags=imported_document['tags']
        )
        model.DBSession.flush_all()
        tg.flash('Document successfully imported!')
        return redirect(tg.url('/document', params=dict(workspace=workspace)))