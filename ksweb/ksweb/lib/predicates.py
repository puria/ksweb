# -*- coding: utf-8 -*-
from bson import ObjectId
from tg import request
from tg.predicates import Predicate


class CanManageEntityOwner(Predicate):
    def __init__(self, msg, field, entity_model):
        super(CanManageEntityOwner, self).__init__(msg)
        self.field = field
        self.entity_model = entity_model

    def evaluate(self, environ, credentials):
        entity_id = request.params.get(self.field)

        if not entity_id and hasattr(request, 'json_body'):
            #  Try to find commercial_farm_id into body if request are a post
            entity_id = request.json_body.get(self.field, None)

        entity = self.entity_model.query.find({'_id': ObjectId(entity_id)}).first()
        if entity and entity._owner == credentials['user']._id:
            return

        self.unmet()
