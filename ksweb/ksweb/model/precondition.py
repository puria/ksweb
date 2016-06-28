# -*- coding: utf-8 -*-
"""Precondition model module."""
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass

from ksweb.model import DBSession, Qa


class Precondition(MappedClass):
    PRECONDITION_TYPE = [u"simple", u"advanced"]
    PRECONDITION_OPERATOR = ['and', 'or', 'not', '(', ')']

    class __mongometa__:
        session = DBSession
        name = 'preconditions'
        indexes = [
            ('_owner',),
        ]

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    title = FieldProperty(s.String, required=False)
    type = FieldProperty(s.OneOf(*PRECONDITION_TYPE), required=True)
    condition = FieldProperty(s.Anything)
    """
    In case of type: simple
    the condition is like: [ObjectId('qa'), 'String_response']

    In case of type advanced
    the condition is like: [ObjectId(precond_1), &, ObjectId(precond_2), | , ObjectId(precond_3)]
    """

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    @property
    def evaluate(self):
        if self.type == 'simple':
            print "evaluate simple precondition"
            return
        if self.type == 'advanced':
            print "evaluate advanced precondition"
            return

    @property
    def response_interested(self):
        res_dict = {}
        if self.type == 'simple':
            qa = Qa.query.get(_id=self.condition[0])
            res_dict[str(qa._id)] = qa
            return res_dict

        for cond in self.condition:
            if cond in Precondition.PRECONDITION_OPERATOR:
                continue
            else:
                rel_ent = Precondition.query.get(_id=cond)
                res_dict.update(rel_ent.response_interested)

        return res_dict

__all__ = ['Precondition']
