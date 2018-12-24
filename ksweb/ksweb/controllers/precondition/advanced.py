# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
from __future__ import print_function
import json

import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from ksweb.lib.utils import get_related_entities_for_filters
from ksweb.model import Precondition
from tg import expose, validate, RestController, decode_params, \
    validation_errors_response, request, response, tmpl_context, flash, lurl
from tg import require
from tg import session
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tw2.core import LengthValidator, StringLengthValidator
from ksweb.lib.validator import WorkspaceExistValidator, PreconditionExistValidator


class PreconditionAdvancedController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"
        tmpl_context.sidebar_precondition_advanced = "preconditions-advanced"

    @expose()
    def get_all(self, workspace, **kw):
        tg.redirect('/precondition', params=dict(workspace=workspace))

    @expose('ksweb.templates.precondition.advanced.new')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def new(self, workspace, **kw):
        return dict(precondition={}, workspace=workspace)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'workspace': WorkspaceExistValidator(required=True),
        'conditions': LengthValidator(min=1, required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, workspace, conditions, **kw):
        error, condition = self._marshall_complex_filter(conditions)
        if error:
            response.status_code = 412
            return dict(errors=error)

        user = request.identity['user']
        Precondition(
            _owner=user._id,
            _workspace=ObjectId(workspace),
            title=title,
            type='advanced',
            condition=condition
        )

        flash(_("Now you can create an output <a href='%s'>HERE</a>" % lurl('/output?workspace='+ str(workspace))))
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': PreconditionExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'workspace': WorkspaceExistValidator(required=True),
        'conditions': LengthValidator(min=1, required=True),
    }, error_handler=validation_errors_response)
    @require(
        CanManageEntityOwner(
            msg=l_(u'You are not allowed to edit this filter.'),
            field='_id',
            entity_model=Precondition))
    def put(self, _id, title, workspace, conditions, **kw):
        error, condition = self._marshall_complex_filter(conditions)
        if error:
            response.status_code = 412
            return dict(errors=error)

        check = self.get_related_entities(_id)

        if check.get("entities"):
            entity = dict(
                _id=_id,
                title=title,
                condition=list(map(str, condition)),
                _workspace=workspace,
                auto_generated=False,
                entity='precondition/advanced',
            )
            session['entity'] = entity  # overwrite always same key for avoiding conflicts
            session.save()
            return dict(redirect_url=tg.url('/resolve', params=dict(workspace=workspace)))

        precondition = Precondition.query.get(_id=ObjectId(_id))
        precondition.title = title
        precondition.condition = condition
        precondition.auto_generated = False
        precondition.status = Precondition.STATUS.UNREAD
        precondition._workspace = workspace

        return dict(errors=None, redirect_url=None)

    @expose('ksweb.templates.precondition.advanced.new')
    @validate({
        '_id': PreconditionExistValidator(),
        'workspace': WorkspaceExistValidator(),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this filter.'), field='_id',
                                  entity_model=Precondition))
    def edit(self, _id, workspace=None, **kw):
        precondition = Precondition.query.get(ObjectId(_id))
        return dict(precondition=precondition, workspace=workspace, errors=None)

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        return get_related_entities_for_filters(_id)

    def _marshall_complex_filter(self, filters):
        boolean_str = ""
        marshalled_filter = []

        for _f in filters:
            if _f['type'] == 'precondition':
                p = Precondition.query.get(ObjectId(_f['content']))
                error = None if p else {'conditions': _('Filter not found.')}
                boolean_str += "True "
                marshalled_filter.append(ObjectId(_f['content']))
            elif _f['type'] == 'operator':
                o = _f['content'] in Precondition.PRECONDITION_OPERATOR
                error = None if o else {'conditions': _('Filter not found.')}
                boolean_str += _f['content'] + " "
                marshalled_filter.append(_f['content'])
            else:
                error = {'conditions': _('Invalid operator')}

        try:
            eval(boolean_str)
        except SyntaxError as e:
            error = {'conditions': _('Syntax error')}

        return error, marshalled_filter
