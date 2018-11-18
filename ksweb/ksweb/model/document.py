# -*- coding: utf-8 -*-
"""Document model module."""
import json

import tg
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty
from ksweb.model import DBSession, User
from ksweb.model.mapped_entity import MappedEntity, TriggerExtension


class Document(MappedEntity):
    class __mongometa__:
        session = DBSession
        name = 'documents'
        indexes = [
            ('_owner',),
            ('public',),
            ('title',),
            ('_category',),
            ('html', 'text')
        ]
        extensions = [TriggerExtension]

    def custom_title(self):
        return Markup("<a href='%s'>%s</a>" % (tg.url('/document/edit',
                                               params=dict(_id=self._id,
                                                           workspace=self._category)),
                                               self.title))

    def content_preview(self):
        from ksweb.lib.utils import five_words
        return five_words(self.html)

    __ROW_COLUM_CONVERTERS__ = {
        'title': custom_title,
        'content': content_preview
    }

    html = FieldProperty(s.String, required=True, if_missing='')
    description = FieldProperty(s.String, required=False)
    license = FieldProperty(s.String, required=False)
    version = FieldProperty(s.String, required=False)
    tags = FieldProperty(s.Anything, required=False)

    @classmethod
    def document_available_for_user(cls, user_id, workspace=None):
        return User.query.get(_id=user_id).owned_entities(cls, workspace)

    @property
    def entity(self):
        return 'document'

    @property
    def children(self):
        from ksweb.lib.utils import get_entities_from_str
        outputs, __ = get_entities_from_str(self.html)
        return outputs

    @property
    def content(self):
        return [{'content': str(__._id), 'title': __.title, 'type': 'output'} for __ in self.children]

    def exportable_dict(self):
        filter_out = ['_category', '_owner', 'created_at', '_id']
        filter_json = {k: v for k, v in self.__json__().items() if k not in filter_out}
        for __ in ['outputs', 'advanced_preconditions', 'qa', 'simple_preconditions']:
            filter_json[__] = {}
        return filter_json

    def export_items(self):
        items = set()
        [items.update(__.export_items()) for __ in self.children]
        items.discard(None)
        return items

    def __group_export_items_by_type(self):
        from itertools import groupby
        items = list(self.export_items())
        items.sort(key=lambda __: __.entity)
        return {k: list(v) for k, v in groupby(items, lambda __: __.entity)}

    def export(self):
        json_result = self.exportable_dict()
        items = self.__group_export_items_by_type()
        content_types = {'qa': 'qa',
                         'output': 'outputs',
                         'precondition/simple': 'simple_preconditions',
                         'precondition/advanced': 'advanced_preconditions'}
        for entity_name, export_name in content_types.items():
            for __ in items.get(entity_name, []):
                json_result[export_name][str(__._id)] = __.exportable_dict()

        return json_result


__all__ = ['Document']
