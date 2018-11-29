# -*- coding: utf-8 -*-
"""Output model module."""
from itertools import filterfalse

import pymongo
import tg
from bson import ObjectId
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ksweb.model import DBSession, User
from ksweb.model.mapped_entity import MappedEntity, TriggerExtension


class Output(MappedEntity):

    class __mongometa__:
        session = DBSession
        name = 'output'
        indexes = [
            ('title',),
            ('html', 'text'),
            ('hash',),
        ]
        extensions = [TriggerExtension]

    def custom_title(self):
        url = tg.url('/output/edit', params=dict(_id=self._id, workspace=self._workspace))
        auto = 'bot' if self.auto_generated else ''
        return Markup("<span class='%s'></span><a href='%s' class='%s'>%s</a>" % (self.status, url, auto, self.title))

    def markup_filter(self):
        return Markup(self.precondition)

    def content_preview(self):
        from ksweb.lib.utils import five_words
        return five_words(self.html)

    __ROW_COLUM_CONVERTERS__ = {
        'title': custom_title,
        'precondition': markup_filter,
        'content': content_preview
    }

    html = FieldProperty(s.String, required=True, if_missing='')
    _precondition = ForeignIdProperty('Precondition')
    precondition = RelationProperty('Precondition')

    @classmethod
    def output_available_for_user(cls, user_id, workspace=None):
        return User.query.get(_id=user_id).owned_entities(cls, workspace).sort([
                                ('auto_generated', pymongo.ASCENDING),
                                ('status', pymongo.DESCENDING),
                                ('title', pymongo.ASCENDING),
                        ])

    @property
    def human_readable_content(self):
        return self.content

    @property
    def entity(self):
        return 'output'

    @property
    def is_filtered(self):
        return True if self._precondition else False

    @property
    def nested_outputs(self):
        def type_filter(item):
            return item['type'] != 'output'
        return list(filterfalse(type_filter, self.content))

    @property
    def dependencies(self):
        return self.dependent_outputs()

    @property
    def content(self):
        from ksweb.lib.utils import get_entities_from_str
        outputs, answers = get_entities_from_str(self.html)
        content = [{'content': str(__._id), 'title': __.title, 'type': 'output'} for __ in outputs]
        content.extend([{'content': str(__._id), 'title': __.title, 'type': 'qa_response'} for __ in answers])
        return content

    @property
    def children(self):
        from ksweb.lib.utils import get_entities_from_str
        outputs, answers = get_entities_from_str(self.html)
        return outputs + answers

    def export_items(self):
        items = set([self])
        if self.precondition:
            items.update(self.precondition.export_items())
        for __ in self.children:
            items.update(__.export_items())
        return items

    def render(self, evaluations_dict):
        if str(self._id) not in evaluations_dict:
            return ''
        if evaluations_dict[str(self._id)]['evaluation'] is False:
            return ''

        from ksweb.lib.utils import TemplateOutput
        nested_output_html = dict()

        for elem in self.nested_outputs:
            nested_output = Output.query.get(_id=ObjectId(elem['content']))
            nested_output_html[elem['content']] = nested_output.render(evaluations_dict)

        ret = TemplateOutput(self.html).safe_substitute(**nested_output_html)
        return ret

    def insert_content(self, entity):
        self.content.append(dict(
            content=str(entity._id),
            title=entity.title,
            type=entity.entity
        ))

    def exportable_dict(self):
        editable = super().exportable_dict()
        if self._precondition:
            editable['_precondition'] = self.precondition.hash
        return editable


__all__ = ['Output']
