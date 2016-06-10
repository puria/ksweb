# -*- coding: utf-8 -*-
"""Precondition controller module"""
import tg
from tg import expose, predicates, redirect, validate, flash, url
from tg.decorators import paginate
from tg.i18n import lazy_ugettext as l_

# from tg.i18n import ugettext as _
# from tg import predicates

# from ksweb.model import DBSession
from ksweb import model
from .simple import PreconditionSimpleController
from ksweb.lib.base import BaseController


class PreconditionController(BaseController):
    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    simple = PreconditionSimpleController()

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