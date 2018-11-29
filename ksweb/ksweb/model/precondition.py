# -*- coding: utf-8 -*-
"""Precondition model module."""
from __future__ import print_function

import pymongo
from bson import ObjectId
from ming import schema as s
from ming.odm import FieldProperty
from markupsafe import Markup
from ksweb.model import DBSession
import tg

from ksweb.model.mapped_entity import MappedEntity, TriggerExtension


def _custom_title(obj):
    url = tg.url('/%s/edit' % (obj.entity), params=dict(_id=obj._id, workspace=obj._workspace))
    cls = 'bot' if obj.auto_generated else ''
    status = obj.status
    return Markup("<span class='%s'></span><a href='%s' class='%s'>%s</a>" % (status, url, cls, obj.title))


def _content_preview(obj):
    return Markup("Little preview of: %s" % obj._id)


class Precondition(MappedEntity):
    class TYPES:
        SIMPLE = u'simple'
        ADVANCED = u'advanced'

    PRECONDITION_TYPE = [TYPES.SIMPLE, TYPES.ADVANCED]
    PRECONDITION_OPERATOR = ['and', 'or', 'not', '(', ')']
    PRECONDITION_CONVERTED_OPERATOR = ['&', '|', 'not', '(', ')']

    class __mongometa__:
        session = DBSession
        name = 'preconditions'
        indexes = [
            ('_owner',),
            ('title',),
            ('hash',),
        ]
        extensions = [TriggerExtension]

    __ROW_COLUM_CONVERTERS__ = {
        'title': _custom_title,
        'content': _content_preview
    }

    type = FieldProperty(s.OneOf(*PRECONDITION_TYPE), required=True)
    condition = FieldProperty(s.Anything)
    """
    In case of type: simple
    the condition is like: [ObjectId('qa'), 'String_response']
    
    A special case of a simple filter is when the string is empty, that means 'Question just answered'
    the condition is like: [ObjectId('qa'), '']

    In case of type advanced
    the condition is like: [ObjectId(precond_1), 'and', ObjectId(precond_2), 'or' , ObjectId(precond_3)]
    """

    @classmethod
    def available_for_user(cls, user_id, workspace):
        return cls.query.find({'_owner': user_id, 'visible': True, '_workspace': ObjectId(workspace)})\
                        .sort([
                                ('auto_generated', pymongo.ASCENDING),
                                ('status', pymongo.DESCENDING),
                                ('title', pymongo.ASCENDING),
                        ])

    @property
    def is_simple(self):
        return self.type == self.TYPES.SIMPLE

    @property
    def is_advanced(self):
        return self.type == self.TYPES.ADVANCED

    @property
    def response_interested(self):
        res_dict = {}

        if self.is_simple:
            qa = self.get_qa()
            if not qa:
                return dict()
            res_dict[str(qa._id)] = qa
            if qa.parent_precondition:
                res_dict.update(qa.parent_precondition.response_interested)
            return res_dict

        for ___ in self.condition:
            if ___ in Precondition.PRECONDITION_OPERATOR:
                continue
            else:
                rel_ent = Precondition.query.get(___)
                res_dict.update(rel_ent.response_interested)

        return res_dict

    def get_qa(self):
        if self.is_advanced:
            return None
        from . import Qa
        return Qa.query.get(self.condition[0])

    @property
    def simple_text_response(self):
        return self.type == self.TYPES.SIMPLE and self.condition[1] == ""

    @property
    def multiple_choice_response(self):
        if self.is_advanced: return False
        qa = self.get_qa()
        return qa.is_multi

    @property
    def single_choice_response(self):
        if self.is_advanced: return False
        qa = self.get_qa()
        return qa.is_single

    @property
    def entity(self):
        return 'precondition/simple' if self.is_simple else 'precondition/advanced'

    @property
    def children(self):
        return [Precondition.query.get(_id=__) for __ in self.condition if __ not in Precondition.PRECONDITION_OPERATOR]

    def export_items(self):
        items = set([self])
        if self.is_advanced:
            items.update(self.children)
        else:
            items.add(self.get_qa())
        return items


__all__ = ['Precondition']
