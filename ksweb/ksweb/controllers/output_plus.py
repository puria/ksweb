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

        title = first_5_words
        output = model.Output(
            _owner=user._id,
            _category=workspace,
            title=title,
            content=content,
            public=True,
            visible=True,
            html=highlighted_text,
            auto_generated=True
        )
        return dict(_id=str(output._id), title=title)
