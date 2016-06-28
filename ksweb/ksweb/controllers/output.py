# -*- coding: utf-8 -*-
"""Output controller module"""
from bson import ObjectId
from tg import expose, validate, validation_errors_response, RestController, decode_params, request, tmpl_context, \
    response
import tg
from tg.decorators import paginate
from tg.i18n import lazy_ugettext as l_
from tg import predicates
from tw2.core import StringLengthValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, PreconditionExistValidator, \
    OutputExistValidator, OutputContentValidator


class OutputController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "outputs"

    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.output.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    def get_all(self, **kw):
        return dict(
            page='output-index',
            fields={
                'columns_name': ['Nome', 'Categoria', 'Precondizione', 'Testo'],
                'fields_name': ['title', 'category', 'precondition', 'content']
            },
            entities=model.Output.query.find().sort('title'),
            actions=True
        )

    @expose('json')
    @expose('ksweb.templates.output.new')
    def new(self, **kw):
        return dict(output={}, errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'content': OutputContentValidator(),
        'category': CategoryExistValidator(required=True),
        'precondition': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def post(self, title, content, category, precondition, **kw):
        """
        #  Check content precondition element
        precond = model.Precondition.query.find({'_id': ObjectId(precondition)}).first()
        related_qa = precond.response_interested
        #  Check elem['content'] contain the obj id of the related
        for elem in content:
            if elem['type'] == 'qa_response':
                if elem['content'] not in related_qa.keys():
                    response.status_code = 412
                    return dict(errors={'content': 'Domanda non legata alla precondizione utilizzata'})
        """

        user = request.identity['user']
        model.Output(
            _owner=user._id,
            _category=ObjectId(category),
            _precondition=ObjectId(precondition),
            title=title,
            content=content,
            public=True,
            visible=True
        )
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': OutputExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'content': OutputContentValidator(),
        'category': CategoryExistValidator(required=True),
        'precondition': PreconditionExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def put(self, _id, title, content, category, precondition,  **kw):
        """
        #  Check content precondition element
        precond = model.Precondition.query.find({'_id': ObjectId(precondition)}).first()
        related_qa = precond.response_interested
        #  Check elem['content'] contain the obj id of the related
        for elem in content:
            if elem['type'] == 'qa_response':
                if elem['content'] not in related_qa.keys():
                    response.status_code = 412
                    return dict(errors={'content': 'Domanda %s non legata alla precondizione utilizzata' % elem['title']})
        """

        output = model.Output.query.find({'_id': ObjectId(_id)}).first()

        output.title = title
        output._category = ObjectId(category)
        output._precondition = ObjectId(precondition)
        output.content = content

        return dict(errors=None)

    @expose('ksweb.templates.output.new')
    @validate({
        'id': OutputExistValidator(required=True)
    }, error_handler=validation_errors_response)
    def edit(self, id, **kw):
        output = model.Output.query.find({'_id': ObjectId(id)}).first()
        return dict(output=output, errors=None)

    @expose('json')
    def sidebar_output(self):
        res = model.Output.query.aggregate([
            {
                '$match': {'visible': True}
            },
            {
                '$group': {
                    '_id': '$_category',
                    'output': {'$push': "$$ROOT",}
                }
            }
        ])['result']

        #  Insert category name into res
        for e in res:
            e['category_name'] = model.Category.query.get(_id=ObjectId(e['_id'])).name

        return dict(outputs=res)

    @expose('json')
    @decode_params('json')
    @validate({
        'id': OutputExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def output_human_readable_details(self, id,  **kw):
        output = model.Output.query.get(_id=ObjectId(id))

        return dict(output={
            '_id': output._id,
            'title': output.title,
            'content': output.human_readbale_content,
            'human_readbale_content': output.human_readbale_content,
            '_owner': output._owner,
            'owner': output.owner.display_name,
            '_precondition': output._precondition,
            'precondition': output.precondition.title,
            '_category': output._category,
            'category': output.category.name,
            'public': output.public,
            'visible': output.visible,
            'created_at': output.created_at
        })
