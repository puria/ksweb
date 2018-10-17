# -*- coding: utf-8 -*-
import re

import tg
from bson import ObjectId
from ksweb.lib.utils import to_object_id
from tg import expose, validate, validation_errors_response, RestController, decode_params, request, tmpl_context, \
    response
from tg import predicates
from tg.decorators import paginate, require
from tg.i18n import lazy_ugettext as l_, ugettext as _
from tw2.core import StringLengthValidator

from ksweb.lib.predicates import CanManageEntityOwner
from ksweb.lib.validator import WorkspaceExistValidator, PreconditionExistValidator, \
    OutputExistValidator, OutputContentValidator
from ksweb.model import Precondition, Output, Document, Category as Workspace


class OutputController(RestController):
    def _validate_precondition_with_qa(self, precondition, html):
        if not precondition:
            return

        _filter = Precondition.query.get(_id=ObjectId(precondition))
        answers = re.findall(r'%%([^\W]+)\b', html)
        problematic = set(answers) - set(_filter.response_interested)
        if len(problematic):
            response.status_code = 412
            return dict(errors={'content': _('The question/s %s is not related to the filter') % problematic})

    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "outputs"
        tmpl_context.id_obj = kw.get('_id')

    allow_only = predicates.has_any_permission('manage', 'lawyer',  msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.output.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def get_all(self, workspace, **kw):
        return dict(
            page='output-index',
            fields={
                'columns_name': [_('Label'), _('Filter'), _('Content')],
                'fields_name': ['title', 'precondition', 'content']
            },
            entities=Output.output_available_for_user(request.identity['user']._id, workspace),
            actions=False,
            workspace=workspace
        )

    @expose('json')
    @expose('ksweb.templates.output.new')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def new(self, workspace, **kw):
        tmpl_context.sidebar_output = "output-new"
        return dict(output={'_precondition': kw.get('precondition_id', None), 'html': ''}, workspace=workspace, errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'html': StringLengthValidator(min=2, required=True, strip=False),
        'workspace': WorkspaceExistValidator(required=True),
        'precondition': PreconditionExistValidator(),
    }, error_handler=validation_errors_response)
    def post(self, title, workspace, html, precondition=None, **kw):
        if precondition:
            error = self._validate_precondition_with_qa(precondition, html)
            if error:
                response.status_code = 412
                return error

        user = request.identity['user']
        o = Output(
            _owner=user._id,
            _category=ObjectId(workspace),
            _precondition=to_object_id(precondition),
            title=title,
            public=True,
            visible=True,
            status=Output.STATUS.UNREAD,
            html=html,
        )
        o.update_content()
        return dict(errors=None)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': OutputExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'html': OutputContentValidator(required=True, strip=False),
        'workspace': WorkspaceExistValidator(required=True),
        'precondition': PreconditionExistValidator(),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this output.'), field='_id', entity_model=Output))
    def put(self, _id, title, html, workspace, precondition=None, **kw):
        if precondition:
            error = self._validate_precondition_with_qa(precondition, html)
            if error:
                response.status_code = 412
                return error

        check = self.get_related_entities(_id)

        # if check.get("entities"):
        #     entity = dict(
        #         _id=_id,
        #         title=title,
        #         _category=to_object_id(workspace),
        #         _precondition=to_object_id(precondition),
        #         entity='output',
        #         auto_generated=False,
        #         html=html
        #     )
        #     session['entity'] = entity  # overwrite always same key for avoiding conflicts
        #     session.save()
        #     return dict(redirect_url=tg.url('/resolve', params=dict(workspace=workspace)))

        output = Output.query.find({'_id': ObjectId(_id)}).first()
        output.title = title
        output._category = ObjectId(workspace)
        output._precondition = to_object_id(precondition)
        output.html = html
        output.auto_generated = False
        output.status = Output.STATUS.UNREAD
        output.update_content()

        return dict(errors=None, redirect_url=None)

    @expose('ksweb.templates.output.new')
    @validate({
        '_id': OutputExistValidator(required=True),
        'workspace': WorkspaceExistValidator(required=True),
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this output.'), field='_id', entity_model=Output))
    def edit(self, _id, workspace, **kw):
        output = Output.query.find({'_id': ObjectId(_id), '_category': ObjectId(workspace)}).first()
        tmpl_context.sidebar_output = "output-edit"
        return dict(output=output, workspace=workspace, errors=None)


    @expose('json')
    def sidebar_output(self, _id=None, workspace=None):  # pragma: no cover
        res = list(Output.query.aggregate([
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
                    'output': {'$push': "$$ROOT", }
                }
            }
        ]))

        #  Insert category name into res
        for e in res:
            e['category_name'] = Workspace.query.get(_id=ObjectId(e['_id'])).name

        return dict(outputs=res)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': OutputExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id,  **kw):
        output = Output.query.get(_id=ObjectId(_id))

        return dict(output={
            '_id': output._id,
            'title': output.title,
            'content': output.human_readbale_content,
            'human_readable_content': output.human_readable_content,
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
        output_related = Output.query.find({"content.type": "output", "content.content": _id}).all()
        documents_related = Document.query.find({"content.type": "output", "content.content": _id}).all()
        entities = list(output_related + documents_related)
        return dict(entities=entities, len=len(entities))

    @expose('json')
    @validate({'workspace': WorkspaceExistValidator(required=True)})
    def mark_as_read(self, workspace):
        Output.mark_as_read(request.identity['user']._id, workspace)
