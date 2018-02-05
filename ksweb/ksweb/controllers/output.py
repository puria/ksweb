# -*- coding: utf-8 -*-
"""Output controller module"""
import json

from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from tg import expose, validate, validation_errors_response, RestController, decode_params, request, tmpl_context, \
    response, flash, lurl
import tg
from tg import session
from tg.decorators import paginate, require
from tg.i18n import lazy_ugettext as l_, ugettext as _
from tg import predicates
from tw2.core import StringLengthValidator, LengthValidator, All
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, PreconditionExistValidator, \
    OutputExistValidator, OutputContentValidator


class OutputController(RestController):
    def _validate_precondition_with_qa(self, precondition, content):
        if not precondition:
            return dict()
        #  Check content precondition element
        precond = model.Precondition.query.find({'_id': ObjectId(precondition)}).first()
        related_qa = precond.response_interested
        #  Check elem['content'] contain the obj id of the related
        for elem in content:
            if elem['type'] == 'qa_response':
                if elem['content'] not in related_qa.keys():
                    response.status_code = 412
                    return dict(errors={'content': _('The question %s is not related to the filter') % elem['title']})
        return dict()

    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "outputs"
        tmpl_context.id_obj = kw.get('_id')

    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.output.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': CategoryExistValidator(required=True)})
    def get_all(self, workspace, **kw):
        return dict(
            page='output-index',
            fields={
                'columns_name': [_('Label'), _('Filter'), _('Content')],
                'fields_name': ['title', 'precondition', 'content']
            },
            entities=model.Output.output_available_for_user(request.identity['user']._id, workspace),
            actions=False,
            workspace=workspace
        )

    @expose('json')
    @expose('ksweb.templates.output.new')
    @validate({'workspace': CategoryExistValidator(required=True)})
    def new(self, workspace, **kw):
        tmpl_context.sidebar_output = "output-new"
        return dict(output={'_precondition': kw.get('precondition_id', None)}, workspace=workspace, errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'content': OutputContentValidator(),
        'ks_editor': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'precondition': PreconditionExistValidator(),
    }, error_handler=validation_errors_response)
    def post(self, title, content, category, precondition, **kw):
        content = content or []

        #  Check content precondition element
        error = self._validate_precondition_with_qa(precondition, content)
        if error:
            return error

        user = request.identity['user']
        model.Output(
            _owner=user._id,
            _category=ObjectId(category),
            _precondition=ObjectId(precondition),
            title=title,
            content=content,
            public=True,
            visible=True,
            html=kw['ks_editor']
        )
        flash(l_("Select the document for you outputs <a href='%s'>HERE</a>" % lurl('/document')))
        return dict(errors=None)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': OutputExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'content': OutputContentValidator(),
        'category': CategoryExistValidator(required=True),
        'precondition': PreconditionExistValidator(),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this output.'), field='_id', entity_model=model.Output))
    def put(self, _id, title, content, category, precondition, **kw):
        content = content or []

        #  Check content precondition element
        error = self._validate_precondition_with_qa(precondition, content)
        if error:
            return error

        check = self.get_related_entities(_id)

        if check.get("entities"):
            entity = dict(
                _id=_id,
                title=title,
                content=content,
                _category=category,
                _precondition=precondition,
                entity='output',
                html=kw['ks_editor']
            )
            session['entity'] = entity  # overwrite always same key for avoiding conflicts
            session.save()
            return dict(redirect_url=tg.url('/resolve', params=dict(workspace=category)))

        output = model.Output.query.find({'_id': ObjectId(_id)}).first()
        output.title = title
        output._category = ObjectId(category)
        output._precondition = ObjectId(precondition)
        output.content = content
        output.html = kw['ks_editor']

        return dict(errors=None, redirect_url=None)

    @expose('ksweb.templates.output.new')
    @validate({
        '_id': OutputExistValidator(required=True),
        'workspace': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this output.'), field='_id', entity_model=model.Output))
    def edit(self, _id, workspace, **kw):
        output = model.Output.query.find({'_id': ObjectId(_id), '_category': ObjectId(workspace)}).first()
        tmpl_context.sidebar_output = "output-edit"
        return dict(output=output, workspace=workspace, errors=None)


    @expose('json')
    def sidebar_output(self, _id=None, workspace=None): #pragma: no cover
        res = list(model.Output.query.aggregate([
            {
                '$match': {
                    '_owner': request.identity['user']._id,
                    '_id': {'$ne': ObjectId(_id)},
                    'visible': True,
                    '_category': ObjectId(workspace)
                }
            },
            {
                '$group': {
                    '_id': '$_category',
                    'output': {'$push': "$$ROOT",}
                }
            }
        ]))

        #  Insert category name into res
        for e in res:
            e['category_name'] = model.Category.query.get(_id=ObjectId(e['_id'])).name

        return dict(outputs=res)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': OutputExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id,  **kw):
        output = model.Output.query.get(_id=ObjectId(_id))

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

    @decode_params('json')
    @expose('json')
    def get_related_entities(self, _id):
        """
        This method return ALL entities (Output, Document) that have inside a `content.content` the given _id
        :param _id:
        :return:
        """
        output_related = model.Output.query.find({"content.type": "output", "content.content": _id}).all()
        documents_related = model.Document.query.find({"content.type": "output", "content.content": _id}).all()
        entities = list(output_related + documents_related)
        return dict(entities=entities, len=len(entities))
