# -*- coding: utf-8 -*-
"""OutputPlus controller module"""
from bson import ObjectId
from ksweb.controllers.resolve import ResolveController
from tg import expose, RestController, predicates, request, decode_params
from ksweb import model


class OutputPlusController(RestController):
    # Uncomment this line if your controller requires an authenticated user
    allow_only = predicates.not_anonymous()

    @expose('json')
    @decode_params('json')
    def post(self, highlighted_text=u'', list_=None):
        first_5_worlds = u' '.join(highlighted_text.split())
        first_5_worlds = u' '.join(first_5_worlds.split(" ")[:5])

        user = request.identity['user']
        category = model.Category.query.find({'name': 'Altro'}).first()

        qa = model.Qa(
                _owner=user._id,
                _category=category._id,
                _parent_precondition=None,
                title=u'Domanda per l\'Output ' + first_5_worlds,
                question=u'Inserisci ' + first_5_worlds,
                tooltip=None,
                link=None,
                type='multi',
                answers=[u'Attiva ' + first_5_worlds],
                public=True,
                visible=True)

        precondition = model.Precondition(
            _owner=user._id,
            _category=category._id,
            title=u'Filtro per l\'Output ' + first_5_worlds,
            type='simple',
            condition=[qa._id, u'Attiva ' + first_5_worlds])

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


        title = u'Output ' + first_5_worlds
        output = model.Output(
            _owner=user._id,
            _category=category._id,
            _precondition=precondition._id,
            title=title,
            content=content,
            public=True,
            visible=True,
            html=highlighted_text
        )
        return dict(_id=str(output._id), title=title)

