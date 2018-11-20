# -*- coding: utf-8 -*-
import hashlib

import ming
from bson import ObjectId
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty, state, mapper, MapperExtension

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

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

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
        return cls.query.find({'status': cls.STATUS.UNREAD, '_category': ObjectId(workspace_id)}).count() or ''

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
        return lurl('/%s/edit/' % self.entity, params=dict(workspace=self.category._id, _id=self._id))

    @classmethod
    def by_id(cls, _id):
        return cls.query.get(_id=ObjectId(_id))

    @classmethod
    def by_hash(cls, _hash):
        return cls.query.get(hash=_hash)

    @classmethod
    def mark_as_read(cls, user_oid, workspace_id):
        from ming.odm import mapper
        collection = mapper(cls).collection.m.collection
        collection.update_many({'_owner': user_oid, 'status': cls.STATUS.UNREAD, '_category': ObjectId(workspace_id)},
                               update={'$set': {'status': cls.STATUS.READ}})

    def dependent_filters(self):
        from ksweb.model import Precondition
        simple = Precondition.query.find(dict(condition=self._id)).all()
        simple_id = [_._id for _ in simple]
        advanced = Precondition.query.find(dict(category=self._category, condition={'$in': simple_id})).all()
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
        filter_out = ['_category', '_owner', 'created_at', 'auto_generated', 'status']
        return {k: v for k, v in self.__json__().items() if k not in filter_out}
