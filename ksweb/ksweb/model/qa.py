# -*- coding: utf-8 -*-
"""Qa model module."""
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass

from ksweb.model import DBSession


class Qa(MappedClass):
    QA_TYPE = [u"text", u"single", u"multi"]

    class __mongometa__:
        session = DBSession
        name = 'qas'
        indexes = [
            ('_owner',),
            ('_category',),
        ]

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    title = FieldProperty(s.String, required=True)
    question = FieldProperty(s.String, required=True)
    tooltip = FieldProperty(s.String, required=False)
    type = FieldProperty(s.OneOf(*QA_TYPE), required=True)
    answers = FieldProperty(s.Anything)

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)


__all__ = ['Qa']
