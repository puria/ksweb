# -*- coding: utf-8 -*-
"""Document model module."""
import tg
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from ksweb.model import DBSession


def _custom_title(obj):
    return Markup("<a href='%s'>%s</a>" % (tg.url('/document/edit', params=dict(_id=obj._id)), obj.title))


def _content_preview(obj):
    return " ".join(Markup(obj.html).striptags().split()[:5])


class Document(MappedClass):
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

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    title = FieldProperty(s.String, required=True)

    html = FieldProperty(s.String, required=True, if_missing='')

    content = FieldProperty(s.Anything, required=True)

    """
    Possible content of the document is a list with two elements type:
        - text
        - output

        If the type is text the content contain the text
        If the type is output the content contain the obj id of the related output


        An example of the content is this
        "content" : [
            {
                "content" : "575eb879c42d7518bb972256",
                "type" : "output",
                "title" : "ciao"
            },
        ]
    """

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    @classmethod
    def document_available_for_user(cls, user_id):
        return cls.query.find({'_owner': user_id}).sort('title')

    @property
    def entity(self):
        return 'document'

    @property
    def upcast(self):
        from ksweb.lib.utils import _upcast

        """
        This property replace widget placeholder into html widget

        {output_589066e6179280afa788035e}
            ->
        <span class="objplaceholder output-widget output_589066e6179280afa788035e"></span>
        """
        return _upcast(self)

    def __json__(self):
        from ksweb.lib.utils import to_dict
        _dict = to_dict(self)
        _dict['entity'] = self.entity
        return _dict


__all__ = ['Document']
