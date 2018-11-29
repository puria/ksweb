# -*- coding: utf-8 -*-
import hashlib

import ming
import pymongo
from bson import ObjectId
from ksweb.model import DBSession
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty, mapper, MapperExtension

from ming.odm.declarative import MappedClass
from tg import lurl, jsonify
from tg.util import Bunch
from tg.util.ming import dictify


def calculate_hash(e):
    prop_names = [prop.name for prop in mapper(e).properties
                  if isinstance(prop, ming.odm.property.FieldProperty)]
    for attr in ["hash", "_id", "tags"]:
        if attr in prop_names: prop_names.remove(attr)
    entity = {k: getattr(e, k) for k in prop_names}
    entity_string = jsonify.encode(entity).encode()
    return 'k' + hashlib.blake2b(entity_string, digest_size=6).hexdigest()


class TriggerExtension(MapperExtension):
    def before_insert(self, instance, st, sess):
        instance.hash = calculate_hash(instance)

    def before_update(self, instance, st, sess):
        instance.hash = calculate_hash(instance)


class MappedEntity(MappedClass):
    STATUS = Bunch(
        READ="READ",
        UNREAD="UNREAD"
    )

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _workspace = ForeignIdProperty('Workspace')
    workspace = RelationProperty('Workspace')

    hash = FieldProperty(s.String)
    title = FieldProperty(s.String, required=True)
    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)
    status = FieldProperty(s.OneOf(*STATUS.values()), required=True, if_missing=STATUS.UNREAD)
    auto_generated = FieldProperty(s.Bool, if_missing=False)

    @property
    def created_at(self):
        return self._id.generation_time

    @classmethod
    def unread_count(cls, workspace_id):
        return cls.query.find({'status': cls.STATUS.UNREAD, '_workspace': ObjectId(workspace_id)}).count() or ''

    @property
    def dependencies(self):
        return []

    @property
    def descendants(self):
        return []

    @property
    def entity(self):
        return ''

    @property
    def url(self):
        return lurl('/%s/edit/' % self.entity, params=dict(workspace=self.workspace._id, _id=self._id))

    @classmethod
    def by_id(cls, _id):
        return cls.query.get(ObjectId(_id))

    @classmethod
    def upsert(cls, find, replace):
        # find_and_modify or other methods does not work for ming mapper extensions
        # so this is an artisan upsert implementation with instant flushes out of uow
        found = cls.query.get(**find)
        if not found:
            o = cls(**replace)
            DBSession.flush(o)
            return o

        for k, v in replace.items():
            found[k] = v
        DBSession.flush(found)
        return found

    @classmethod
    def by_hash(cls, _hash):
        return cls.query.get(hash=_hash)

    @classmethod
    def mark_as_read(cls, user_oid, workspace_id):
        from ming.odm import mapper
        collection = mapper(cls).collection.m.collection
        collection.update_many({'_owner': user_oid, 'status': cls.STATUS.UNREAD, '_workspace': ObjectId(workspace_id)},
                               update={'$set': {'status': cls.STATUS.READ}})

    @classmethod
    def available_for_user(cls, user_id, workspace=None):
        from ksweb.model import User
        return User.query.get(_id=user_id).owned_entities(cls, workspace).sort([
            ('auto_generated', pymongo.ASCENDING),
            ('status', pymongo.DESCENDING),
            ('title', pymongo.ASCENDING),
        ])

    def dependent_filters(self):
        from ksweb.model import Precondition
        simple = Precondition.query.find(dict(condition=self._id)).all()
        simple_id = [_._id for _ in simple]
        advanced = Precondition.query.find(dict(workspace=self._workspace, condition={'$in': simple_id})).all()
        return simple + advanced

    def dependent_outputs(self):
        from ksweb.model import Output
        outputs = Output.query.find({'content.content': str(self._id)}).all()
        return outputs

    def __json__(self):
        _dict = dictify(self)
        _dict['entity'] = self.entity
        return _dict

    def exportable_dict(self):
        filter_out = ['_workspace', '_owner', 'created_at', 'auto_generated', 'status', '_id']
        return {k: v for k, v in self.__json__().items() if k not in filter_out}
