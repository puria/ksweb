# -*- coding: utf-8 -*-
"""Qa model module."""
import tg
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ming.odm.icollection import InstrumentedList
from ksweb.model import DBSession


def _format_instrumented_list(l):
        return ', '.join(l)


def _custom_title(obj):
    return Markup(
        "<a href='%s'>%s</a>" % (tg.url('/qa/edit', params=dict(_id=obj._id)), obj.title))


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

    # __ROW_TYPE_CONVERTERS__ = {
    #     #InstrumentedObj: _format_instrumented_obj,
    #     InstrumentedList: _format_instrumented_list,
    # }

    __ROW_COLUM_CONVERTERS__ = {
        'title': _custom_title,
    }

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    _parent_precondition = ForeignIdProperty('Precondition')
    parent_precondition = RelationProperty('Precondition')

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

    @property
    def entity(self):
        return 'qa'

    @property
    def is_text(self):
        return self.type == self.QA_TYPE[0]

    @property
    def is_single(self):
        return self.type == self.QA_TYPE[1]

    @property
    def is_multi(self):
        return self.type == self.QA_TYPE[2]

    def __json__(self):
        from ksweb.lib.utils import to_dict
        _dict = to_dict(self)
        _dict['entity'] = self.entity
        return _dict


__all__ = ['Qa']
