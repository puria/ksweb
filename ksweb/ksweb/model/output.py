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
from ksweb.model.mapped_entity import MappedEntity


def _custom_title(obj):
    url = tg.url('/output/edit', params=dict(_id=obj._id, workspace=obj._category))
    auto = 'bot' if obj.auto_generated else ''
    status = obj.status
    return Markup("<span class='%s'></span><a href='%s' class='%s'>%s</a>" % (status, url, auto, obj.title))


def _content_preview(obj):
    if not obj:
        return " "
    return " ".join(Markup(obj.html).striptags().split()[:5])

def _custom_filter(o):
    return Markup(o.precondition)

class Output(MappedEntity):

    class __mongometa__:
        session = DBSession
        name = 'output'
        indexes = [
            ('title',),
        ]

    __ROW_COLUM_CONVERTERS__ = {
        'title': _custom_title,
        'precondition': _custom_filter,
        'content': _content_preview
    }

    html = FieldProperty(s.String, required=True, if_missing='')
    content = FieldProperty(s.Anything, if_missing=[])
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

    def render(self, evaluations_dict):
        if str(self._id) not in evaluations_dict:
            return ''
        if evaluations_dict[str(self._id)]['evaluation'] is False:
            return ''

        from ksweb.lib.utils import TemplateOutput
        nested_output_html = dict()

        for elem in self.nested_outputs:
            nested_output = Output.query.get(_id=ObjectId(elem['content']))
            nested_output_html['output_' + elem['content']] = nested_output.render(evaluations_dict)

        ret = TemplateOutput(self.html).safe_substitute(**nested_output_html)
        return ret

    def insert_content(self, entity):
        self.content.append(dict(
            content=str(entity._id),
            title=entity.title,
            type=entity.entity
        ))

    def update_content(self):
        from ksweb.lib.utils import get_entities_from_str
        outputs, answers = get_entities_from_str(self.html)
        self.content = [{'content': str(__._id), 'title': __.title, 'type': 'output'} for __ in outputs]
        self.content.extend([{'content': str(__._id), 'title': __.title, 'type': 'qa_response'} for __ in answers])

    @classmethod
    def update_content_titles_with(cls, entity):
        related = cls.query.find({'content.content': str(entity._id)}, ).all()
        for document in related:
            for i, item in enumerate(document.content):
                if item.content == str(entity._id):
                    document.content[i].title = entity.title


__all__ = ['Output']
