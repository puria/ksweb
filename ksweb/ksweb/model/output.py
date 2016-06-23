# -*- coding: utf-8 -*-
"""Output model module."""
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from datetime import datetime
from ksweb.model import DBSession


class Output(MappedClass):

    class __mongometa__:
        session = DBSession
        name = 'output'
        indexes = [
            ('title',),
        ]

    __ROW_TYPE_CONVERTERS__ = {}

    _id = FieldProperty(s.ObjectId)

    title = FieldProperty(s.String, required=True)
    content = FieldProperty(s.Anything, required=True)
    """
    Possible content of the output is a list with two elements type:
        - text
        - Response of the Preconditions questions

        but for the moment is really simple text ;)

    """
    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _precondition = ForeignIdProperty('Precondition')
    precondition = RelationProperty('Precondition')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    created_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow())

    @property
    def human_readbale_content(self):
        #  TODO: Non appena saranno aggiornati gli output, bisogna modificare questa property affinche restituisca dei valori leggibili

        #res = []
        #for elem in self.content:
            #if elem is testo ok
            # else mostra una stringa di dettaglio della precondizione
        return self.content

__all__ = ['Output']
