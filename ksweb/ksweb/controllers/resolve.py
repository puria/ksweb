# -*- coding: utf-8 -*-
"""Output controller module"""
from bson import ObjectId
from formencode.validators import OneOf
from ksweb.lib.base import BaseController
from ksweb.lib.predicates import CanManageEntityOwner
from ksweb.lib.utils import to_object_id, clone_obj
from tg import abort
from tg import expose, validate, validation_errors_response, RestController, decode_params, request, tmpl_context, \
    response
import tg
from tg import flash
from tg import redirect
from tg.decorators import paginate, require
from tg.i18n import lazy_ugettext as l_
from tg import predicates
from tw2.core import StringLengthValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, PreconditionExistValidator, \
    OutputExistValidator, OutputContentValidator, ConditionValidator


class ResolveController(BaseController):

    related_models = {
        'output': model.Output,
        'precondition/simple': model.Precondition,
        'precondition/advanced': model.Precondition,
        'qa': model.Qa
    }

    @decode_params('json')
    @expose('ksweb.templates.resolve.index')
    def index(self, **kw):
        return dict(**kw)

    # TODO: custom validation....
    @decode_params('json')
    @validate({
          #'_id': OutputExistValidator(required=True),
         'condition': ConditionValidator(required=False),
         'title': StringLengthValidator(min=2),
         'content': OutputContentValidator(required=False),
         '_category': CategoryExistValidator(required=True),
         '_precondition': PreconditionExistValidator(required=False),
        }, error_handler=abort(404, error_handler=True))
    @expose()
    def original_edit(self, **kw):
        print "original_edit ===========================================================", kw

        self._original_edit(**kw)

        flash(u'Entità modificata correttamente!')

        return redirect(base_url='/')

    @expose('json')
    @decode_params('json')
    @validate({
         '_id': OutputExistValidator(required=True),
         'title': StringLengthValidator(min=2),
         'content': OutputContentValidator(),
         'condition': ConditionValidator(required=False),
         '_category': CategoryExistValidator(required=True),
         '_precondition': PreconditionExistValidator(required=True),
        }, error_handler=validation_errors_response)
    def _original_edit(self, **kw):
        print "_original_edit", kw

        kw['_category'] = to_object_id(kw.get('_category'))
        kw['_precondition'] = to_object_id(kw.get('_precondition'))
        kw.pop('entity', None)

        entity = self._get_entity(kw['entity'], kw['_id'])

        for k, v in kw.items():
            setattr(entity, k, v)

        # TODO: update..
        self._find_and_modify(kw)

        return entity

    @decode_params('json')
    @validate({
        #'_id': OutputExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'content': OutputContentValidator(required=False),
        'condition': ConditionValidator(required=False),
        '_category': CategoryExistValidator(required=True),
        '_precondition': PreconditionExistValidator(required=False),
    }, error_handler=abort(404, error_handler=True))
    @expose()
    def clone_object(self, **kw):
        self._clone_object(**kw)
        flash("%s creato correttamente!" % kw['entity'])
        return redirect(base_url='/%s' % kw['entity'])

    @expose('json')
    @decode_params('json')
    @expose('json')
    @decode_params('json')
    @validate({
         '_id': OutputExistValidator(required=True),
         'title': StringLengthValidator(min=2),
         'content': OutputContentValidator(),
         '_category': CategoryExistValidator(required=True),
         '_precondition': PreconditionExistValidator(required=True),
        }, error_handler=validation_errors_response)
    def _clone_object(self, **kw):

        print "_clone_object", kw

        entity = self._get_entity(kw['entity'], kw['_id'])

        # TODO: REMOVE
        kw['title'] += ' [NUOVO]'

        new_obj = clone_obj(self.related_models[kw['entity']], entity, kw)

        return new_obj


    @decode_params('json')
    @validate({
        #'_id': OutputExistValidator(mod=True),
        'title': StringLengthValidator(min=2),
        'content': OutputContentValidator(required=False),
        'condition': ConditionValidator(required=False),
        '_category': CategoryExistValidator(required=True),
        '_precondition': PreconditionExistValidator(required=False),
    }, error_handler=abort(404, error_handler=True))
    @expose('ksweb.templates.resolve.manually_resolve')
    def manually_resolve(self, **kw):

        return dict(
            entity=kw['entity'],
            values=kw
        )

    @decode_params('json')
    @expose('json')
    def mark_resolved(self, obj=None, list_to_new=None, list_to_old=None, **kw):

        entity = self._get_entity(obj['entity'], obj['_id'])

        if len(list_to_new) >= 1:
            # modifico l'oggetto e lascio quelli della lista invariati
            if len(list_to_old) >= 1:
                # ho degli oggetti che puntano al vecchio, devo clonare
                print "ho degli oggetti che puntano sia al vecchio che al nuovo, devo clonare"
                self._clone_and_modify_(obj, list_to_new)
            else:
                # posso modificare semplicemente l'oggetto, tanto non ci sono + oggetti che puntano al vecchio
                print "posso modificare semplicemente l'oggetto, tanto non ci sono + oggetti che puntano al vecchio"
                self._original_edit(**obj)
        else:
            # tutti gli oggetti puntano al veccho

            print "tutti gli oggetti puntano al veccho"
            self._original_edit(**obj)

        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        """
        This method return ALL entities (Output, Document) that have inside a `content.content` the given _id
        :param _id:
        :return:
        """
        output_related = model.Output.query.find({"content.type": "output", "content.content": _id}).all()
        documents_related = model.Document.query.find({"content.type": "output", "content.content": _id}).all()

        print "get_related_entities"
        print "output related", [o.title for o in output_related], len(output_related), type(output_related)
        print "document related", [d.title for d in documents_related], len(documents_related), type(documents_related)

        entities = list(output_related + documents_related)



        return {
            'entities': entities,
            'len': len(entities)
        }

    def _get_entity(self, entity_name, _id):
        model_ = self.related_models[entity_name]
        return model_.query.get(_id=ObjectId(_id))

    def _clone_and_modify_(self, obj_to_clone, to_edit):
        new_obj = self._clone_object(**obj_to_clone)

        for obj in to_edit:
            entity = self._get_entity(obj['entity'], obj['_id'])

            if obj_to_clone['entity'] == 'output':
                # I have to search into:
                #     output.content
                #     document.content
                for elem in entity.content:
                    if elem['content'] == obj_to_clone['_id']:
                        elem['content'] = str(getattr(new_obj, '_id'))
                        elem['title'] = getattr(new_obj, 'title')

            elif obj_to_clone['entity'] == 'precondition/simple':
                # I have to search into:
                #     qa._parent_precondition
                #     output._precondition
                #     precondition.condition
                if entity.entity == 'qa' and entity._parent_precondition == ObjectId(obj_to_clone['_id']):
                    entity._parent_precondition = new_obj._id
                elif entity.entity == 'output' and entity._precondition == ObjectId(obj_to_clone['_id']):
                    entity._precondition = new_obj._id
                elif entity.entity == 'precondition/advanced':
                    for index, elem in enumerate(entity.condition):
                        if elem == ObjectId(obj_to_clone['_id']):
                            entity.condition[index] = new_obj._id





    def _find_and_modify(self, obj_dict):

        """
        Update `title` inside of sub-document
        :param obj:
        :param _id:
        :return:
        """

        for entity in self.get_related_entities(obj_dict['_id'])['entities']:
            for elem in entity.content:
                if elem['content'] == obj_dict['_id']:
                    elem['title'] = obj_dict['title']

