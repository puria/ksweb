# -*- coding: utf-8 -*-
"""Document controller module"""
import tg
from bson import ObjectId
from tg import expose, tmpl_context, predicates, RestController, request, validate, flash, response, validation_errors_response
from tg.decorators import paginate, decode_params
from tg.i18n import lazy_ugettext as l_

# from ksweb.model import DBSession
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
                'columns_name': ['Name', 'Category', 'Content'],
                'fields_name': ['title', 'category', 'content']
            },
            entities=model.Document.query.find().sort('title'),
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

        user = request.identity['user']
        model.Document(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            content=content,
            public=True,
            visible=True
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
    def put(self, _id, title, content, category,  **kw):
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()

        document.title = title
        document._category = ObjectId(category)
        document.content = content

        return dict(errors=None)

    @expose('ksweb.templates.document.new')
    @validate({
        'id': DocumentExistValidator(required=True)
    }, error_handler=validation_errors_response)
    def edit(self, id, **kw):
        tmpl_context.sidebar_document = "document-new"
        document = model.Document.query.find({'_id': ObjectId(id)}).first()
        return dict(document=document, errors=None)