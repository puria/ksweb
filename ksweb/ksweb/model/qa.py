# -*- coding: utf-8 -*-
"""Qa model module."""
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ming.odm.icollection import InstrumentedList
from ksweb.model import DBSession


def _format_instrumented_list(l):
        return ', '.join(l)


class Qa(MappedClass):
    QA_TYPE = [u"text", u"single", u"multi"]

    class __mongometa__:
        session = DBSession
        name = 'qas'
        indexes = [
            ('title',),
            ('_owner',),
            ('_category',),
            ('type', 'public',),
        ]

    __ROW_TYPE_CONVERTERS__ = {
        #InstrumentedObj: _format_instrumented_obj,
        InstrumentedList: _format_instrumented_list,
    }

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    title = FieldProperty(s.String, required=True)
    question = FieldProperty(s.String, required=True)
    tooltip = FieldProperty(s.String, required=False)
    link = FieldProperty(s.String, required=False)
    type = FieldProperty(s.OneOf(*QA_TYPE), required=True)

    answers = FieldProperty(s.Anything)

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    @classmethod
    def qa_available_for_user(cls, user_id):
        return cls.query.find({'_owner': user_id}).sort('title')

__all__ = ['Qa']
