# -*- coding: utf-8 -*-
from bson import ObjectId
from ksweb.lib.utils import entity_from_id
from tg import expose, RestController, predicates, request, decode_params
from ksweb.model import Output


class OutputPlusController(RestController):
    allow_only = predicates.not_anonymous()

    @expose('json')
    @decode_params('json')
    def post(self, highlighted_text=u'', workspace=None, list_=[]):
        first_5_words = u' '.join(highlighted_text.split())
        title = u' '.join(first_5_words.split(" ")[:5])
        user = request.identity['user']
        output = Output(
            _owner=user._id,
            _category=workspace,
            title=title,
            content=[],
            public=True,
            visible=True,
            html=highlighted_text,
            auto_generated=True,
            status=Output.STATUS.UNREAD,
        )
        for o in list_:
            m = entity_from_id(_id=ObjectId(o[2:-1]))
            output.insert_content(m)

        return dict(_id=str(output._id), title=title)
