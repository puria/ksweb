# -*- coding: utf-8 -*-
"""Qa model module."""

import tg
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ksweb.model import DBSession
from ksweb.model.mapped_entity import MappedEntity, TriggerExtension
from tg.i18n import ugettext as _


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
            ('_workspace',),
            ('type', 'public',),
            ('hash',),
        ]
        extensions = [TriggerExtension]

    def custom_title(self):
        url = tg.url('/qa/edit', params=dict(_id=self._id, workspace=self._workspace))
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

    def update_dependencies(self, old):
        from ksweb.model import Output
        outputs = Output.query.find({'$text': {'$search': old}}).all()
        for o in outputs:
            old_hash = o.hash
            o.html = o.html.replace(old, self.hash)
            DBSession.flush(o)
            o.update_dependencies(old_hash)
        self.generate_output_from()

    def __get_common_fields(self, **kwargs):
        common = dict(
            _owner=self._owner,
            _workspace=self._workspace,
            public=self.public,
            visible=self.visible
        )
        common.update(**kwargs)
        return common

    def __generate_generic_filter_from(self, title, **kwargs):
        from ksweb.model import Precondition
        common = self.__get_common_fields(auto_generated=True, status=Precondition.STATUS.UNREAD)
        common.update(**kwargs)
        common.update({'title': title})
        return Precondition.upsert({'title': title}, common)

    def generate_text_filter_from(self):
        from ksweb.model import Precondition
        return self.__generate_generic_filter_from(
            title=_(u'%s \u21d2 was compiled' % self.title),
            type=Precondition.TYPES.SIMPLE,
            condition=[self._id, ""]
        )

    def generate_filter_answer_from(self, answer):
        from ksweb.model import Precondition
        return self.__generate_generic_filter_from(
            title=u'%s \u21d2 %s' % (self.title, answer),
            type=Precondition.TYPES.SIMPLE,
            condition=[self._id, answer],
        )

    def invalidate_outdated_filters(self):
        simple_filters = [f for f in self.dependent_filters() if f.is_simple]
        broken_filters = [f for f in simple_filters for c in f.condition if isinstance(c, str) and c not in self.answers]
        for f in broken_filters:
            from ksweb.model import Precondition
            f.status = Precondition.STATUS.INCOMPLETE

    def generate_filters_from(self):
        if self.is_text:
            return self.generate_text_filter_from()

        composed_condition = []
        for __ in self.answers:
            composed_condition.append(self.generate_filter_answer_from(__)._id)
            composed_condition.append('or')
        del composed_condition[-1]
        self.invalidate_outdated_filters()
        from ksweb.model import Precondition
        return self.__generate_generic_filter_from(
            title=_(u'%s \u21d2 was compiled' % self.title),
            type=Precondition.TYPES.ADVANCED,
            condition=composed_condition
        )

    def generate_output_from(self):
        from ksweb.model import Output
        _filter = self.generate_filters_from()
        common = self.__get_common_fields()
        title = u'%s \u21d2 output' % self.title
        common.update({'_precondition': _filter._id, 'html': '@{%s}' % self.hash, 'title': title})
        o = Output.upsert({'title': title}, common)
        o.auto_generated = True
        o.status = Output.STATUS.UNREAD
        return o

    def export_items(self):
        items = set([self])
        if self.parent_precondition:
            items.update(self.parent_precondition.export_items())
        return items

    def exportable_dict(self):
        editable = super().exportable_dict()
        if self.parent_precondition:
            editable['_parent_precondition'] = self.parent_precondition.hash
        return editable


__all__ = ['Qa']
