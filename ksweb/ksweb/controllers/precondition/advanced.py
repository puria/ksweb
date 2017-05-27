# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
import json

import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from tg import expose, validate, RestController, decode_params, \
    validation_errors_response, request, response, tmpl_context, flash, lurl
from tg import require
from tg import session
from tg.i18n import ugettext as _, lazy_ugettext as l_
from tw2.core import LengthValidator, StringLengthValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, PreconditionExistValidator


class PreconditionAdvancedController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"
        tmpl_context.sidebar_precondition_advanced = "preconditions-advanced"

    @expose('ksweb.templates.precondition.advanced.new')
    @validate({'workspace': CategoryExistValidator(required=True)})
    def new(self, workspace, **kw):
        return dict(precondition={}, workspace=workspace)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'conditions': LengthValidator(min=1, required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, category, conditions, **kw):

        bool_str = ""
        condition = []

        # TODO refactor this
        for cond in conditions:
            if cond['type'] == 'precondition':
                #  Check if precondition exist
                precond = model.Precondition.query.get(_id=ObjectId(cond['content']))
                if not precond:
                    response.status_code = 412
                    return dict(errors={'conditions': _('Filter not found.')})

                bool_str += "True "
                condition.append(ObjectId(cond['content']))

            elif cond['type'] == 'operator':
                if not cond['content'] in model.Precondition.PRECONDITION_OPERATOR:
                    response.status_code = 412
                    return dict(errors={'conditions': _('Invalid logic operator.')})

                bool_str += cond['content']+" "
                condition.append(cond['content'])

            else:
                response.status_code = 412
                return dict(errors={'conditions': _('Invalid operator')})

        try:
            res_eval = eval(bool_str)
        except SyntaxError as e:
            response.status_code = 412
            return dict(errors={'conditions': _('Syntax error.')})

        user = request.identity['user']
        model.Precondition(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            type='advanced',
            condition=condition
        )

        flash(_("Now you can create an output <a href='%s'>HERE</a>" % lurl('/output?workspace='+ str(category))))
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': PreconditionExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'conditions': LengthValidator(min=1, required=True),
    }, error_handler=validation_errors_response)
    @require(
        CanManageEntityOwner(
            msg=l_(u'You are not allowed to edit this filter.'),
            field='_id',
            entity_model=model.Precondition))
    def put(self, _id, title, category, conditions, **kw):
        bool_str = ""
        condition = []

        # TODO refactor this
        for cond in conditions:
            if cond['type'] == 'precondition':
                #  Check if precondition exist
                precond = model.Precondition.query.get(_id=ObjectId(cond['content']))
                if not precond:
                    response.status_code = 412
                    return dict(errors={'conditions': _('Filter not found.')})

                bool_str += "True "
                condition.append(ObjectId(cond['content']))

            elif cond['type'] == 'operator':
                if not cond['content'] in model.Precondition.PRECONDITION_OPERATOR:
                    response.status_code = 412
                    return dict(errors={'conditions': _('Invalid logic operator.')})

                bool_str += cond['content']+" "
                condition.append(cond['content'])

            else:
                response.status_code = 412
                return dict(errors={'conditions': _('Invalid operator')})

        try:
            res_eval = eval(bool_str)
        except SyntaxError as e:
            response.status_code = 412
            return dict(errors={'conditions': _('Syntax error')})

        check = self.get_related_entities(_id)

        if check.get("entities"):
            print "condition", condition
            entity = dict(
                _id=_id,
                title=title,
                condition=map(str, condition),
                _category=category,
                entity='precondition/advanced',
            )
            session['entity'] = entity  # overwrite always same key for avoiding conflicts
            session.save()
            return dict(redirect_url=tg.url('/resolve'))

        precondition = model.Precondition.query.get(_id=ObjectId(_id))
        precondition.title = title
        precondition.condition = condition
        precondition._category = category

        return dict(errors=None, redirect_url=None)

    @expose('ksweb.templates.precondition.advanced.new')
    @validate({
        '_id': PreconditionExistValidator(),
        'workspace': CategoryExistValidator(),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this filter.'), field='_id',
                                  entity_model=model.Precondition))
    def edit(self, _id, workspace=None, **kw):
        precondition = model.Precondition.query.find({'_id': ObjectId(_id)}).first()
        return dict(precondition=precondition, workspace=workspace, errors=None)

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        """
        This method return ALL entities (Output, Preconditions, Qas) that have inside the given _id
        :param _id:
        :return:
        """

        outputs_related = model.Output.query.find({'_precondition': ObjectId(_id)}).all()
        preconditions_related = model.Precondition.query.find({'type': 'advanced', 'condition': ObjectId(_id)}).all()
        qas_related = model.Qa.query.find({"_parent_precondition": ObjectId(_id)}).all()

        entities = list(outputs_related + preconditions_related + qas_related)

        return {
            'entities': entities,
            'len': len(entities)
        }
