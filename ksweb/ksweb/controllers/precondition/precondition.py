# -*- coding: utf-8 -*-
"""Precondition controller module"""

from tg import expose, predicates, redirect, validate, flash, url
from tg.i18n import lazy_ugettext as l_

# from tg.i18n import ugettext as _
# from tg import predicates

# from ksweb.model import DBSession
from .simple import PreconditionSimpleController
from ksweb.lib.base import BaseController


class PreconditionController(BaseController):
    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    simple = PreconditionSimpleController()

    @expose('ksweb.templates.precondition.index')
    def index(self, **kw):
        return dict(page='precondition-index')
