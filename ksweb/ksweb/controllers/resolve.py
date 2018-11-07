# -*- coding: utf-8 -*-
"""Output controller module"""
import tg
from bson import ObjectId
from ksweb.lib.base import BaseController
from ksweb.lib.utils import to_object_id, clone_obj, with_entity_session, entity_from_id
from ksweb.lib.validator import WorkspaceExistValidator
from tg import expose, decode_params, flash, redirect, session
from ksweb import model
from tg import validate
from tg.i18n import ugettext as _, lazy_ugettext as l_


class ResolveController(BaseController):

    related_models = {
        'output': model.Output,
        'precondition/simple': model.Precondition,
        'precondition/advanced': model.Precondition,
        'qa': model.Qa,
        'document': model.Document
    }

    @expose('ksweb.templates.resolve.index')
    @decode_params('json')
    @with_entity_session
    @validate({'workspace': WorkspaceExistValidator(required=True), })
    def index(self, workspace, **kw):
        return dict(workspace=workspace, **kw)

    @expose()
    @with_entity_session
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def original_edit(self, workspace, **kw):
        entity = self._original_edit()
        session.delete()
        flash(_(u'Entity %s successfully edited!') % entity.title)
        return redirect(base_url=tg.url('/%s' % entity.entity, params=dict(workspace=workspace)))

    @expose()
    @with_entity_session
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def clone_object(self, workspace, **kw):
        entity = self._clone_object()
        session.delete()
        flash(_("%s successfully created!") % entity.title)
        return redirect(base_url=tg.url('/%s' % entity.entity, params=dict(workspace=workspace)))

    @expose()
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def discard_changes(self, workspace, **kw):
        session.delete()
        flash(_(u'All the edits are discarded'))
        return redirect(base_url=tg.url('/qa', params=dict(workspace=workspace)))

    @expose('ksweb.templates.resolve.manually_resolve')
    @with_entity_session
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def manually_resolve(self, workspace, **kw):
        entity = session.get('entity')

        return dict(
            entity=entity['entity'],
            values=entity,
            workspace=workspace
        )

    @expose('json')
    @decode_params('json')
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
        flash(_(u'All the conflicts are successfully resolved'))
        return dict(errors=None)

    def _original_edit(self):
        params = session.get('entity')
        params['_category'] = to_object_id(params.get('_category'))
        params['_precondition'] = to_object_id(params.get('_precondition'))
        entity = entity_from_id(params['_id'])
        params.pop('entity', None)
        for k, v in params.items():
            setattr(entity, k, v)
        return entity

    def _clone_object(self):
        params = session.get('entity')
        entity = entity_from_id(params['_id'])
        params['title'] += _(' [CLONED]')
        new_obj = clone_obj(self.related_models[params['entity']], entity, params)
        return new_obj

    def _clone_and_modify_(self, obj_to_clone, to_edit):
        new_obj = self._clone_object()
        old_obj_id = ObjectId(obj_to_clone['_id'])
        for obj in to_edit:
            entity = entity_from_id(obj['_id'])
            if obj_to_clone['entity'] == 'output':
                entity.html = entity.html.replace(obj_to_clone['id'], str(new_obj._id))
            elif obj_to_clone['entity'] in ['precondition/simple', 'precondition/advanced']:
                if entity.entity == 'qa' and entity._parent_precondition == old_obj_id:
                    entity._parent_precondition = new_obj._id
                elif entity.entity == 'output' and entity._precondition == old_obj_id:
                    entity._precondition = new_obj._id
                elif entity.entity == 'precondition/advanced':
                    entity.condition = [new_obj._id if __ == old_obj_id else __ for __ in entity.condition]
            elif obj_to_clone['entity'] == 'qa':
                entity.condition = [new_obj._id if __ == old_obj_id else __ for __ in entity.condition]
