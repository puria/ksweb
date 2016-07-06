# -*- coding: utf-8 -*-
"""Precondition controller module"""
import tg
from bson import ObjectId
from tg.decorators import paginate, decode_params, validate
from tg.i18n import lazy_ugettext as l_
from tg import expose, predicates, tmpl_context, validation_errors_response
from ksweb import model
from ksweb.lib.validator import PreconditionExistValidator
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
    def index(self, **kw):
        return dict(
            page='precondition-index',
            fields={
                'columns_name': ['Nome', 'Tipo', 'Proprietario'],
                'fields_name': ['title', 'type', 'owner']
            },
            entities=model.Precondition.query.find({'visible': True}).sort('title'),
            actions=True
        )

    @expose('json')
    def sidebar_precondition(self):
        res = model.Precondition.query.aggregate([
            {
                '$match': {'visible': True}
            },
            {
                '$group': {
                    '_id': '$_category',
                    'precondition': {'$push': "$$ROOT",}
                }
            }
        ])['result']

        #  Insert category name into res
        for e in res:
            e['category_name'] = model.Category.query.get(_id=ObjectId(e['_id'])).name

        return dict(precond=res)

    @expose('json')
    def available_preconditions(self):
        preconditions = Precondition.query.find({'visible': True}).sort('title').all()
        return dict(preconditions=preconditions)

    @expose('json')
    @decode_params('json')
    @validate({
        'id': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def qa_precondition(self, id, **kw):
        precondition = model.Precondition.query.get(_id=ObjectId(id))
        return dict(qas=precondition.response_interested[0])
