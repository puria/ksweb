# -*- coding: utf-8 -*-
"""Qa model module."""
import pymongo

import tg
from bson import ObjectId
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty, MapperExtension
from ksweb.model import DBSession, User
from ksweb.model.mapped_entity import MappedEntity, TriggerExtension
from tg.i18n import ugettext as _


class AutoCompile(MapperExtension):
    def after_insert(self, instance, st, sess):
        from ksweb.model import Precondition
        DBSession.flush_all()

        common_precondition_params = dict(
            _owner=instance._owner,
            _category=ObjectId(instance._category),
            auto_generated=True,
            status=Precondition.STATUS.UNREAD
        )
        if instance.is_text:
            autogen_filter = Precondition(
                                **common_precondition_params,
                                title=_(u'%s \u21d2 was compiled' % instance.title),
                                type=Precondition.TYPES.SIMPLE,
                                condition=[instance.hash, ""]
                            )
        else:
            condition = []
            for answer in instance.answers:
                precondition = Precondition(
                    **common_precondition_params,
                    title=u'%s \u21d2 %s' % (instance.title, answer),
                    type=Precondition.TYPES.SIMPLE,
                    condition=[instance.hash, answer],
                )
                condition.append(precondition.hash)
                condition.append('or')
            del condition[-1]

            autogen_filter = Precondition(
                **common_precondition_params,
                title=instance.title + _(u' \u21d2 was compiled'),
                type=Precondition.TYPES.ADVANCED,
                condition=condition
            )

        if autogen_filter:
            from ksweb.model import Output
            Output(
                **common_precondition_params,
                _precondition=ObjectId(autogen_filter._id),
                title=instance.title + u' \u21d2 output',
                html='@{%s}' % instance.hash,
            )
        DBSession.flush_all()


class Qa(MappedEntity):
    class TYPES:
        TEXT = u'text'
        SINGLE = u'single'
        MULTI = u'multi'

    QA_TYPE = [TYPES.TEXT, TYPES.SINGLE, TYPES.MULTI]

    class __mongometa__:
        session = DBSession
        name = 'qas'
        indexes = [
            ('title',),
            ('_owner',),
            ('_category',),
            ('type', 'public',),
            ('hash',),
        ]
        extensions = [TriggerExtension, AutoCompile]

    def custom_title(self):
        url = tg.url('/qa/edit', params=dict(_id=self._id, workspace=self._category))
        auto = 'bot' if self.auto_generated else ''
        return Markup("<span class='%s'></span><a href='%s' class='%s'>%s</a>" % (self.status, url, auto, self.title))

    __ROW_COLUM_CONVERTERS__ = {
        'title': custom_title,
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
        return User.query.get(_id=user_id).owned_entities(cls, workspace).sort([
                                ('auto_generated', pymongo.ASCENDING),
                                ('status', pymongo.DESCENDING),
                                ('title', pymongo.ASCENDING),
                        ])

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

    @property
    def dependencies(self):
        return self.dependent_filters() + self.dependent_outputs()

    def export_items(self):
        items = set([self])
        if self.parent_precondition:
            items.update(self.parent_precondition.export_items())
        return items


__all__ = ['Qa']
