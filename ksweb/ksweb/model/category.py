# -*- coding: utf-8 -*-
"""Category model module."""
from bson import ObjectId
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ksweb.model import DBSession


class Category(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'categories'
        custom_indexes = [
            dict(fields=('name', '_owner'), unique=True, sparse=True)
        ]

    _id = FieldProperty(s.ObjectId)

    name = FieldProperty(s.String, required=True)
    visible = FieldProperty(s.Bool, if_missing=True, index=True)
    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    @classmethod
    def per_user(cls, user_id):
        return cls.query.find({'_owner': {'$in': [user_id, None]}, 'visible': True}).sort('_id').all()

    @classmethod
    def by_id(cls, _id):
        return cls.query.get(_id=ObjectId(_id))


__all__ = ['Category']
