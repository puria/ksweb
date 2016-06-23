# -*- coding: utf-8 -*-
"""Precondition model module."""
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ksweb.model import DBSession


class Precondition(MappedClass):
    PRECONDITION_TYPE = [u"simple", u"advanced"]

    class __mongometa__:
        session = DBSession
        name = 'preconditions'
        indexes = [
            ('_owner',),
        ]

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    title = FieldProperty(s.String, required=False)
    type = FieldProperty(s.OneOf(*PRECONDITION_TYPE), required=True)
    condition = FieldProperty(s.Anything)
    """
    In case of type: simple
    the condition is like: [ObjectId('qa'), 'String_response']

    In case of type: simple
    the condition is like: [ObjectId('qa'), 'String_response']

    In case of type advanced
    the condition is like: [ObjectId(precond_1), &, ObjectId(precond_2), | , ObjectId(precond_3)]
    """

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    @property
    def evaluate(self):
        if self.type == 'simple':
            print "evaluate simple precondition"
            return
        if self.type == 'advanced':
            print "evaluate advanced precondition"
            return


__all__ = ['Precondition']
