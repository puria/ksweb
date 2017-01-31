# -*- coding: utf-8 -*-
"""Output model module."""
from string import Template

import tg
from markupsafe import Markup
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from datetime import datetime
from ksweb.model import DBSession


def _custom_title(obj):
    return Markup("<a href='%s'>%s</a>" % (tg.url('/output/edit', params=dict(_id=obj._id)), obj.title))


def _content_preview(obj):
    return Markup("Little preview of: %s" % obj._id)


class Output(MappedClass):

    class __mongometa__:
        session = DBSession
        name = 'output'
        indexes = [
            ('title',),
        ]

    __ROW_COLUM_CONVERTERS__ = {
        'title': _custom_title,
        'content': _content_preview
    }

    _id = FieldProperty(s.ObjectId)

    title = FieldProperty(s.String, required=True)
    content = FieldProperty(s.Anything, required=True)
    """
    Possible content of the output is a list with two elements type:
        - text
        - precondition_response

    If the type is text the content contain the text
    If the type is qa_response the content contain the obj id of the related precondition/response


    An example of the content is this
    "content" : [
        {
            "content" : "Simple text",
            "type" : "text",
            "title" : ""
        },
        {
            "content" : "57723171c42d7513bb31e17d",
            "type" : "qa_response",
            "title" : "Colori"
        }
    ]

    """

    html = FieldProperty(s.String, required=True, if_missing='')

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _precondition = ForeignIdProperty('Precondition')
    precondition = RelationProperty('Precondition')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    created_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow())

    @classmethod
    def output_available_for_user(cls, user_id):
        return cls.query.find({'_owner': user_id}).sort('title')

    @property
    def human_readbale_content(self):
        #  TODO: Non appena saranno aggiornati gli output, bisogna modificare questa property affinche restituisca dei valori leggibili

        #res = []
        #for elem in self.content:
            #if elem is testo ok
            # else mostra una stringa di dettaglio del filtro
        return self.content

    @property
    def entity(self):
        return 'output'

    @property
    def upcast(self):
        """
        This property replace widget placeholder into html widget

        {output_589066e6179280afa788035e}
            ->
        <span class="objplaceholder output-widget output_589066e6179280afa788035e"></span>
        """

        from ksweb.lib.helpers import editor_widget_template_for_output, editor_widget_template_for_qa

        values = dict()

        # qa_response and output only
        for c in self.content:
            if c['type'] == 'output':
                values['output_'+c['content']] = editor_widget_template_for_output(id_=c['content'], title=c['title'])
            else:
                # qa_response
                values['qa_'+c['content']] = editor_widget_template_for_qa(id_=c['content'], title=c['title'])

        return Template(self.html).safe_substitute(**values)

    def __json__(self):
        from ksweb.lib.utils import to_dict
        _dict = to_dict(self)
        _dict['entity'] = self.entity
        return _dict


__all__ = ['Output']
