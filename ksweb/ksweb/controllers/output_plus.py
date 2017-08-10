# -*- coding: utf-8 -*-
"""OutputPlus controller module"""
from bson import ObjectId
from ksweb.controllers.resolve import ResolveController
from tg import expose, RestController, predicates, request, decode_params
from tg.i18n import ugettext as _
from ksweb import model


class OutputPlusController(RestController):
    allow_only = predicates.not_anonymous()

    @expose('json')
    @decode_params('json')
    def post(self, highlighted_text=u'', workspace=None, list_=[]):
        first_5_words = u' '.join(highlighted_text.split())
        first_5_words = u' '.join(first_5_words.split(" ")[:5])

        user = request.identity['user']

        qa = model.Qa(
                _owner=user._id,
                _category=workspace,
                _parent_precondition=None,
                title=_(u'Question for Output ') + first_5_words,
                question=_(u'Add ') + first_5_words,
                tooltip=None,
                link=None,
                type='multi',
                answers=[_(u'Start ') + first_5_words],
                public=True,
                visible=True)

        precondition = model.Precondition(
            _owner=user._id,
            _category=workspace,
            title=_(u'Filter for Ouput ') + first_5_words,
            type='simple',
            condition=[qa._id, _(u'Start ') + first_5_words])

        content = []
        for elem in list_:
            type, _id = elem.split("_")
            _model = ResolveController.related_models[type]
            o = _model.query.get(ObjectId(_id))
            content.append({
                'type': type,
                'title': o.title,
                'content': _id
            })

        title = _(u'Output ') + first_5_words
        output = model.Output(
            _owner=user._id,
            _category=workspace,
            _precondition=precondition._id,
            title=title,
            content=content,
            public=True,
            visible=True,
            html=highlighted_text
        )
        return dict(_id=str(output._id), title=title)
