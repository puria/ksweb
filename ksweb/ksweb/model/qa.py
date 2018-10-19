# -*- coding: utf-8 -*-
"""Qa model module."""
import tg
from bson import ObjectId
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ksweb.model import DBSession, User
from ksweb.model.mapped_entity import MappedEntity


def _format_instrumented_list(l):
        return ', '.join(l)


def _custom_title(obj):
    url = tg.url('/qa/edit', params=dict(_id=obj._id, workspace=obj._category))
    auto = 'bot' if obj.auto_generated else ''
    status = obj.status
    return Markup("<span class='%s'></span><a href='%s' class='%s'>%s</a>" % (status, url, auto, obj.title))


class Qa(MappedEntity):
    class TYPES:
        TEXT=u'text'
        SINGLE=u'single'
        MULTI=u'multi'

    QA_TYPE = [TYPES.TEXT, TYPES.SINGLE, TYPES.MULTI]

    class __mongometa__:
        session = DBSession
        name = 'qas'
        indexes = [
            ('title',),
            ('_owner',),
            ('_category',),
            ('type', 'public',),
        ]

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
    def available_for_user(cls, user_id, workspace=None):
        return User.query.get(_id=user_id).owned_entities(cls, workspace)

    @property
    def entity(self):
        return 'qa'

    @property
    def is_text(self):
        return self.type == self.TYPES.TEXT

    @property
    def is_single(self):
        return self.type == self.TYPES.SINGLE

    @property
    def is_multi(self):
        return self.type == self.TYPES.MULTI

__all__ = ['Qa']
