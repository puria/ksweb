# -*- coding: utf-8 -*-
"""Qa model module."""
import tg
from bson import ObjectId
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ming.odm.icollection import InstrumentedList
from ksweb.model import DBSession, User
from ksweb.model.mapped_entity import MappedEntity


def _format_instrumented_list(l):
        return ', '.join(l)


def _custom_title(obj):
    return Markup(
        "<a href='%s'>%s</a>" % (tg.url('/qa/edit', params=dict(_id=obj._id,workspace=obj._category)), obj.title))


class Qa(MappedEntity):
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

    _parent_precondition = ForeignIdProperty('Precondition')
    parent_precondition = RelationProperty('Precondition')

    question = FieldProperty(s.String, required=True)
    tooltip = FieldProperty(s.String, required=False)
    link = FieldProperty(s.String, required=False)
    type = FieldProperty(s.OneOf(*QA_TYPE), required=True)

    answers = FieldProperty(s.Anything)

    @classmethod
    def qa_available_for_user(cls, user_id, workspace=None):
        return User.query.get(_id=user_id).owned_entities(cls, workspace)

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


__all__ = ['Qa']
