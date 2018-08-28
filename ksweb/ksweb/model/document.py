# -*- coding: utf-8 -*-
"""Document model module."""
import tg
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty
from ksweb.model import DBSession, User
from ksweb.model.mapped_entity import MappedEntity


def _custom_title(obj):
    return Markup("<a href='%s'>%s</a>" % (tg.url('/document/edit', params=dict(_id=obj._id, workspace=obj._category)), obj.title))


def _content_preview(obj):
    return " ".join(Markup(obj.html).striptags().split()[:5])


class Document(MappedEntity):
    class __mongometa__:
        session = DBSession
        name = 'documents'
        indexes = [
            ('_owner',),
            ('public',),
            ('title',),
            ('_category',),
        ]

    __ROW_COLUM_CONVERTERS__ = {
        'title': _custom_title,
        'content': _content_preview
    }

    html = FieldProperty(s.String, required=True, if_missing='')
    content = FieldProperty(s.Anything, if_missing=[])
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
    def upcast(self):
        from ksweb.lib.utils import _upcast
        return _upcast(self)

    def update_content(self):
        from ksweb.lib.utils import get_entities_from_str
        outputs, __ = get_entities_from_str(self.html)
        self.content = [{'content': str(__._id), 'title': __.title, 'type': 'output'} for __ in outputs]

    @classmethod
    def update_content_titles_with(cls, entity):
        related = cls.query.find({'content.content': str(entity._id)}, ).all()
        for document in related:
            for i, item in enumerate(document.content):
                if item.content == str(entity._id):
                    document.content[i].title = entity.title


__all__ = ['Document']
