# -*- coding: utf-8 -*-
"""Output controller module"""
from bson import ObjectId
from ksweb.lib.base import BaseController
from ksweb.lib.utils import to_object_id, clone_obj, with_entity_session
from tg import expose, decode_params, flash, redirect, session
from ksweb import model


class ResolveController(BaseController):

    related_models = {
        'output': model.Output,
        'precondition/simple': model.Precondition,
        'precondition/advanced': model.Precondition,
        'qa': model.Qa,
        'document': model.Document
    }

    @decode_params('json')
    @expose('ksweb.templates.resolve.index')
    @with_entity_session
    def index(self, **kw):
        return dict(**kw)

    @expose()
    @with_entity_session
    def original_edit(self, **kw):
        entity = self._original_edit()
        flash(u'Entità %s modificata correttamente!' % entity.title)
        session.delete()
        return redirect(base_url='/')

    @expose()
    @with_entity_session
    def clone_object(self, **kw):
        entity = self._clone_object()
        flash("%s creato correttamente!" % entity.title)
        session.delete()
        return redirect(base_url='/')

    @expose('')
    def discard_changes(self, **kw):
        session.delete()
        flash(u'Tutte le modifiche sono state scartate')
        return redirect(base_url='/')

    @expose('ksweb.templates.resolve.manually_resolve')
    @with_entity_session
    def manually_resolve(self, **kw):

        # fetch params from session
        entity = session.get('entity')

        return dict(
            entity=entity['entity'],
            values=entity
        )

    @decode_params('json')
    @expose('json')
    @with_entity_session
    def mark_resolved(self, list_to_new=None, list_to_old=None, **kw):

        entity = session.get('entity')

        if len(list_to_new) >= 1:
            if len(list_to_old) >= 1:
                # worst case, we have some objects that refer to new and other that refer ro old, need a clone
                self._clone_and_modify_(entity, list_to_new)
            else:
                # we can just edit old object because no one refer more to old object
                self._original_edit()
        else:
            # all objects refer to old, we can just edit old object
            self._original_edit()

        session.delete()
        flash(u'Tutti i conflitti sono stati risolti correttamente')
        return dict(errors=None)

    def _original_edit(self):

        # fetch params from session
        params = session.get('entity')

        # transform to ObjectId here because ObjectId is not JSON serializable
        params['_category'] = to_object_id(params.get('_category'))
        params['_precondition'] = to_object_id(params.get('_precondition'))

        # retrieve original object
        entity = self._get_entity(params['entity'], params['_id'])

        # popping non-related values
        params.pop('entity', None)

        # true edit
        for k, v in params.items():
            setattr(entity, k, v)

        # TODO: update..
        # self._find_and_modify(kw)
        return entity

    def _clone_object(self):
        params = session.get('entity')
        entity = self._get_entity(params['entity'], params['_id'])
        params['title'] += ' [NUOVO]'
        new_obj = clone_obj(self.related_models[params['entity']], entity, params)
        return new_obj

    def _get_entity(self, entity_name, _id):
        model_ = self.related_models[entity_name]
        return model_.query.get(_id=ObjectId(_id))

    def _clone_and_modify_(self, obj_to_clone, to_edit):
        new_obj = self._clone_object()

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

            elif obj_to_clone['entity'] in ['precondition/simple', 'precondition/advanced']:
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

            elif obj_to_clone['entity'] == 'qa':
                # I have to search into:
                #     precondition.condition
                for index, elem in enumerate(entity.condition):
                    if elem == ObjectId(obj_to_clone['_id']):
                        entity.condition[index] = new_obj._id
