# -*- coding: utf-8 -*-
"""Output controller module"""
from bson import ObjectId
from tg import expose, validate, validation_errors_response, response, RestController, decode_params, request, tmpl_context
import tg
from tg.decorators import paginate
from tg.i18n import lazy_ugettext as l_
from tg import predicates
from tw2.core import StringLengthValidator, OneOfValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, QAExistValidator, PreconditionExistValidator


class OutputController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "outputs"

    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.output.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    def get_all(self, **kw):
        return dict(
            page='output-index',
            fields={
                'columns_name': ['Nome', 'Categoria', 'Precondizione', 'Testo'],
                'fields_name': ['title', 'category', 'precondition', 'content']
            },
            entities=model.Output.query.find().sort('title'),
            actions=True
        )

    @expose('json')
    @expose('ksweb.templates.output.new')
    def new(self, **kw):
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'content': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'precondition': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, content, category, precondition,  **kw):

        user = request.identity['user']

        model.Output(
            _owner=user._id,
            _category=ObjectId(category),
            _precondition=ObjectId(precondition),
            title=title,
            content=content,
            public=True,
            visible=True
        )
        return dict(errors=None)

    @expose('json')
    def sidebar_output(self):
        res = model.Output.query.aggregate([
            {
                '$match': {'visible': True}
            },
            {
                '$group': {
                    '_id': '$_category',
                    'output': {'$push': "$$ROOT",}
                }
            }
        ])['result']

        #  Insert category name into res
        for e in res:
            e['category_name'] = model.Category.query.get(_id=ObjectId(e['_id'])).name

        return dict(outputs=res)
