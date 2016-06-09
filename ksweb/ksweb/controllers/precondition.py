# -*- coding: utf-8 -*-
"""Precondition controller module"""

from tg import expose, redirect, validate, flash, url
# from tg.i18n import ugettext as _
# from tg import predicates

from ksweb.lib.base import BaseController
# from ksweb.model import DBSession


class PreconditionController(BaseController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = predicates.not_anonymous()
    
    @expose('ksweb.templates.precondition.index')
    def index(self, **kw):
        return dict(page='precondition-index')

    @expose('ksweb.templates.precondition.new')
    def new(self, **kw):
        return dict(page='precondition-new')
