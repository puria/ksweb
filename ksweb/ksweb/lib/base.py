# -*- coding: utf-8 -*-
"""The base Controller API."""

from tg import TGController, tmpl_context
from tg import request


__all__ = ['BaseController']


class BaseController(TGController):

    def __call__(self, environ, context):
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, context)
