# -*- coding: utf-8 -*-
"""Category model module."""
from ming import schema as s
from ming.odm import FieldProperty
from ming.odm.declarative import MappedClass
from ksweb.model import DBSession


class Category(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'categories'
        indexes = [
            ('pippo',),
            ('visible',),
        ]

    _id = FieldProperty(s.ObjectId)

    name = FieldProperty(s.String, required=True)
    visible = FieldProperty(s.Bool, if_missing=True)

__all__ = ['Category']
