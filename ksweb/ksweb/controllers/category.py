# -*- coding: utf-8 -*-
"""Category controller module"""
from bson import ObjectId
from tg import expose, redirect, validate, flash, url, RestController, validation_errors_response

# from tg.i18n import ugettext as _
# from tg import predicates

# from ksweb.model import DBSession
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator


class CategoryController(RestController):
    # Uncomment this line if your controller requires an authenticated user
    # allow_only = predicates.not_anonymous()
    
    @expose('json')
    @validate({
        'id': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def get_one(self, id,  **kw):
        qa = model.Category.query.get(_id=ObjectId(id))
        return dict(qa=qa)

    @expose('json')
    def get_all(self):
        categories = model.Category.query.find({'visible': True}).all()
        return dict(categories=categories)
