# -*- coding: utf-8 -*-
"""Precondition/simple controller module"""
import json

import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from tg import expose, validate, RestController, decode_params, \
    validation_errors_response, request, response, tmpl_context
from tg import require
from tw2.core import LengthValidator, StringLengthValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, PreconditionExistValidator


class PreconditionAdvancedController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "preconditions"
        tmpl_context.sidebar_precondition_advanced = "preconditions-advanced"

    @expose('ksweb.templates.precondition.advanced.new')
    def new(self, **kw):
        return dict(precondition={})

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
                    return dict(errors={'conditions': 'Precondizione non trovata.'})

                bool_str += "True "
                condition.append(ObjectId(cond['content']))

            elif cond['type'] == 'operator':
                if not cond['content'] in model.Precondition.PRECONDITION_OPERATOR:
                    response.status_code = 412
                    return dict(errors={'conditions': 'Operatore logico non valido.'})

                bool_str += cond['content']+" "
                condition.append(cond['content'])

            else:
                response.status_code = 412
                return dict(errors={'conditions': 'Operatore non valido'})

        try:
            res_eval = eval(bool_str)
        except SyntaxError as e:
            response.status_code = 412
            return dict(errors={'conditions': 'Errore di sintassi.'})

        user = request.identity['user']
        model.Precondition(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            type='advanced',
            condition=condition
        )

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
            msg=u'Non puoi modificare questa precondizione.',
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
                    return dict(errors={'conditions': 'Precondizione non trovata.'})

                bool_str += "True "
                condition.append(ObjectId(cond['content']))

            elif cond['type'] == 'operator':
                if not cond['content'] in model.Precondition.PRECONDITION_OPERATOR:
                    response.status_code = 412
                    return dict(errors={'conditions': 'Operatore logico non valido.'})

                bool_str += cond['content']+" "
                condition.append(cond['content'])

            else:
                response.status_code = 412
                return dict(errors={'conditions': 'Operatore non valido'})

        try:
            res_eval = eval(bool_str)
        except SyntaxError as e:
            response.status_code = 412
            return dict(errors={'conditions': 'Errore di sintassi.'})

        check = self.get_related_entities(_id)

        if check.get("entities"):
            params = dict(
                _id=_id,
                title=title,
                content=json.dumps(dict(), ensure_ascii=False),
                condition=json.dumps(condition, ensure_ascii=False),
                category=category,
                precondition='',
                entity='precondition/advanced',
                **kw
            )
            return dict(redirect_url=tg.url('/resolve', params=params))

        precondition = model.Precondition.query.get(_id=ObjectId(_id))
        precondition.title = title
        precondition.condition = condition
        precondition._category = category

        return dict(errors=None, redirect_url=None)

    @expose('ksweb.templates.precondition.advanced.new')
    @validate({
        '_id': PreconditionExistValidator()
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=u'Non puoi modificare questa precondizione.', field='_id',
                                  entity_model=model.Precondition))
    def edit(self, _id, **kw):
        precondition = model.Precondition.query.find({'_id': ObjectId(_id)}).first()
        return dict(precondition=precondition, errors=None)

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
