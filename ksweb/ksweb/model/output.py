# -*- coding: utf-8 -*-
"""Output model module."""
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ming.odm.icollection import InstrumentedList
from datetime import datetime
from ksweb.model import DBSession


class Output(MappedClass):

    class __mongometa__:
        session = DBSession
        name = 'output'
        indexes = [
            ('title',),
        ]

    __ROW_CONVERTERS__ = {}

    _id = FieldProperty(s.ObjectId)

    title = FieldProperty(s.String, required=True)
    content = FieldProperty(s.Anything, required=True)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _precondition = ForeignIdProperty('Precondition')
    precondition = RelationProperty('Precondition')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    created_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow())

__all__ = ['Output']
