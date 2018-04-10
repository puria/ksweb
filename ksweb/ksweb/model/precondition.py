# -*- coding: utf-8 -*-
"""Precondition model module."""
from __future__ import print_function
from bson import ObjectId
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty
from ming.odm.declarative import MappedClass
from markupsafe import Markup
from ksweb.model import DBSession, Qa
import tg


def _custom_title(obj):
    url = tg.url('/precondition/%s/edit' % ('simple' if obj.is_simple else 'advanced'),
                 params=dict(_id=obj._id, workspace=obj._category))
    cls = 'bot' if obj.auto_generated else ''
    return Markup("<a href='%s' class='%s'>%s</a>" % (url, cls, obj.title))


def _content_preview(obj):
    return Markup("Little preview of: %s" % obj._id)


class Precondition(MappedClass):
    PRECONDITION_TYPE = [u"simple", u"advanced"]
    PRECONDITION_OPERATOR = ['and', 'or', 'not', '(', ')']
    PRECONDITION_CONVERTED_OPERATOR = ['&', '|', 'not', '(', ')']

    class __mongometa__:
        session = DBSession
        name = 'preconditions'
        indexes = [
            ('_owner',),
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

    title = FieldProperty(s.String, required=False)
    type = FieldProperty(s.OneOf(*PRECONDITION_TYPE), required=True)
    auto_generated = FieldProperty(s.Bool, if_missing=False)
    condition = FieldProperty(s.Anything)
    """
    In case of type: simple
    the condition is like: [ObjectId('qa'), 'String_response']

    In case of type advanced
    the condition is like: [ObjectId(precond_1), &, ObjectId(precond_2), | , ObjectId(precond_3)]
    """

    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)

    @classmethod
    def precondition_available_for_user(cls, user_id, workspace=None):
        if workspace:
            return cls.query.find({'_owner': user_id, 'visible': True, '_category': ObjectId(workspace)}).sort('title')
        return cls.query.find({'_owner': user_id, 'visible': True}).sort('title')

    @property
    def evaluate(self):
        if self.type == 'simple':
            print("evaluate simple precondition")
            return
        if self.type == 'advanced':
            print("evaluate advanced precondition")
            return

    @property
    def is_simple(self):
        return self.type == 'simple'

    @property
    def response_interested(self):
        """
        Example of the return value
        {
            '5772314bc42d7513bb31e17c': <Qa title=u'Sesso'
              _category=ObjectId('575581e4c42d75124a0a9601')
              question=u'Di che sesso sei?' tooltip=None visible=True
              _owner=ObjectId('575581e4c42d75124a0a95fc') link=None
              answers=I[u'Maschio', u'Femmina']
              _id=ObjectId('5772314bc42d7513bb31e17c') type=u'single'
              public=True>,
            '57723171c42d7513bb31e17d': <Qa title=u'Colori'
              _category=ObjectId('575581e4c42d75124a0a9602')
              question=u'Che colori ti piacciono?' tooltip=u'che colori
              ti piacciono' visible=True
              _owner=ObjectId('575581e4c42d75124a0a95fc') link=None
              answers=I[u'Rosso', u'Verde', u'Blu', u'Giallo']
              _id=ObjectId('57723171c42d7513bb31e17d') type=u'multi'
              public=True>
        }
        :return:
        """
        res_dict = {}
        if self.type == 'simple':
            qa = Qa.query.get(_id=self.condition[0])
            res_dict[str(qa._id)] = qa
            if qa.parent_precondition:
                res_dict.update(qa.parent_precondition.response_interested)
            return res_dict
        for cond in self.condition:
            if cond in Precondition.PRECONDITION_OPERATOR:
                continue
            else:
                rel_ent = Precondition.query.get(_id=ObjectId(cond))
                print(cond)
                res_dict.update(rel_ent.response_interested)

        return res_dict

    def get_qa(self):
        from . import Qa
        if not self.is_simple:
            return None
        return Qa.query.get(_id=ObjectId(self.condition[0]))

    @property
    def simple_text_response(self):
        return self.type == "simple" and self.condition[1] == ""

    @property
    def multiple_choice_response(self):
        if self.is_simple:
            qa = self.get_qa()
            return qa.is_multi
        return False

    @property
    def single_choice_response(self):
        if self.is_simple:
            qa = self.get_qa()
            return qa.is_single
        return False

    @property
    def entity(self):
        return 'precondition/simple' if self.is_simple else 'precondition/advanced'


    def __json__(self):
        from ksweb.lib.utils import to_dict
        _dict = to_dict(self)
        _dict['entity'] = self.entity
        return _dict


__all__ = ['Precondition']
