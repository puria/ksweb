# -*- coding: utf-8 -*-
"""Precondition model module."""
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass

from ksweb.model import DBSession


class Precondition(MappedClass):
    class __mongometa__:
        session = DBSession
        name = 'preconditions'
        indexes = [
            ('_user',),
        ]

    _id = FieldProperty(s.ObjectId)

    name = FieldProperty(s.String, required=False)

    _user = ForeignIdProperty('User')
    user = RelationProperty('User')


__all__ = ['Precondition']
