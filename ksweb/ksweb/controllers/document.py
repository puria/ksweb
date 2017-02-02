# -*- coding: utf-8 -*-
"""Document controller module"""
import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from tg import expose, tmpl_context, predicates, RestController, request, validate, validation_errors_response
from tg.decorators import paginate, decode_params, require
from tg.i18n import lazy_ugettext as l_, ugettext as _
from tw2.core import StringLengthValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, DocumentExistValidator, DocumentContentValidator


class DocumentController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "documents"

    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.document.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    def get_all(self, **kw):
        return dict(
            page='document-index',
            fields={
                'columns_name': [_('Label'), _('Category'), _('Content')],
                'fields_name': ['title', 'category', 'content']
            },
            entities=model.Document.document_available_for_user(request.identity['user']._id),
            actions=True
        )

    @expose('ksweb.templates.document.new')
    def new(self, **kw):
        tmpl_context.sidebar_document = "document-new"
        return dict(document={}, errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'content': DocumentContentValidator()
    }, error_handler=validation_errors_response)
    def post(self, title, content, category,  **kw):

        if not content:
            content = []

        user = request.identity['user']
        model.Document(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            content=content,
            public=True,
            visible=True,
            html=kw['ks_editor']

        )
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': DocumentExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'content': DocumentContentValidator()
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'), field='_id', entity_model=model.Document))
    def put(self, _id, title, content, category,  **kw):

        if not content:
            content = []

        document = model.Document.query.find({'_id': ObjectId(_id)}).first()

        document.title = title
        document._category = ObjectId(category)
        document.content = content
        document.html = kw['ks_editor']

        return dict(errors=None)

    @expose('ksweb.templates.document.new')
    @validate({
        '_id': DocumentExistValidator(required=True)
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'), field='_id', entity_model=model.Document))
    def edit(self, _id, **kw):
        tmpl_context.sidebar_document = "document-new"
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()
        return dict(document=document, errors=None)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': DocumentExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id, **kw):
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()

        return dict(document=document)
