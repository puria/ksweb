# -*- coding: utf-8 -*-
"""Document controller module"""
import json
from string import Template

import tg
from bson import ObjectId
from ksweb.lib.predicates import CanManageEntityOwner
from tg import expose, tmpl_context, predicates, RestController, request, validate, validation_errors_response
from tg import redirect
from tg import response
from tg.decorators import paginate, decode_params, require
from tg.i18n import lazy_ugettext as l_, ugettext as _
from tw2.core import StringLengthValidator
from ksweb import model
from ksweb.lib.validator import CategoryExistValidator, DocumentExistValidator, DocumentContentValidator
from ksweb.lib.forms import UploadFileForm


class DocumentController(RestController):
    def _before(self, *args, **kw):
        tmpl_context.sidebar_section = "documents"

    allow_only = predicates.has_any_permission('manage', 'lawyer', msg=l_('Only for admin or lawyer'))

    @expose('ksweb.templates.document.index')
    @paginate('entities', items_per_page=int(tg.config.get('pagination.items_per_page')))
    @validate({'workspace': CategoryExistValidator(required=True)})
    def get_all(self, workspace, **kw):
        return dict(
            page='document-index',
            fields={
                'columns_name': [_('Label'), _('Workspace'), _('Content')],
                'fields_name': ['title', 'category', 'content']
            },
            entities=model.Document.document_available_for_user(request.identity['user']._id, workspace=workspace),
            actions=True,
            workspace=workspace,
            download=True
        )

    @expose('ksweb.templates.document.new')
    @validate({'workspace': CategoryExistValidator(required=True)})
    def new(self, workspace, **kw):
        tmpl_context.sidebar_document = "document-new"
        return dict(document={}, workspace=workspace, errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'content': DocumentContentValidator()
    }, error_handler=validation_errors_response)
    def post(self, title, category, content=[], **kw):

        if not content:
            content = []

        user = request.identity['user']
        model.Document(
            _owner=user._id,
            _category=ObjectId(category),
            title=title,
            content=content,
            public=True,
            visible=True,
            html=kw['ks_editor']

        )
        return dict(errors=None)

    @decode_params('json')
    @expose('json')
    @validate({
        '_id': DocumentExistValidator(required=True),
        'title': StringLengthValidator(min=2),
        'category': CategoryExistValidator(required=True),
        'content': DocumentContentValidator()
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'), field='_id',
                                  entity_model=model.Document))
    def put(self, _id, title, content, category, **kw):

        if not content:
            content = []

        document = model.Document.query.find({'_id': ObjectId(_id)}).first()

        document.title = title
        document._category = ObjectId(category)
        document.content = content
        document.html = kw['ks_editor']

        return dict(errors=None)

    @expose('ksweb.templates.document.new')
    @validate({
        '_id': DocumentExistValidator(required=True),
        'workspace': CategoryExistValidator(required=True)
    }, error_handler=validation_errors_response)
    @require(CanManageEntityOwner(msg=l_(u'You are not allowed to edit this document.'), field='_id',
                                  entity_model=model.Document))
    def edit(self, _id, workspace, **kw):
        tmpl_context.sidebar_document = "document-new"
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()
        return dict(document=document, workspace=workspace, errors=None)

    @expose('json')
    @decode_params('json')
    @validate({
        '_id': DocumentExistValidator(required=True),

    }, error_handler=validation_errors_response)
    def human_readable_details(self, _id, **kw):
        document = model.Document.query.find({'_id': ObjectId(_id)}).first()

        return dict(document=document)

    @expose("json", content_type='application/json')
    @validate({
        '_id': DocumentExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def export(self, _id):
        document = model.Document.query.get(_id=ObjectId(_id)).__json__()
        response.headerlist.append(('Content-Disposition', str('attachment;filename=%s.json' % _id)))
        document.pop('_category', None)
        document.pop('_id', None)
        document.pop('entity', None)
        document['outputs'] = {}
        document['advanced_preconditions'] = {}
        document['simple_preconditions'] = {}
        document['qa'] = {}
        for output in document['content']:
            export_outputs(output['content'], document)
        return document

    @expose()
    @validate({
        'workspace': CategoryExistValidator(required=True),
    }, error_handler=validation_errors_response)
    def import_document(self, workspace, file_import):
        imported_document = json.load(file_import.file)
        content = []
        values = {}
        for output in imported_document['content']:
            c = {'type': output['type'], 'title': output['title'], 'content': str(
                import_output(imported_document, str(output['content']), imported_document['_owner'], workspace))}
            content.append(c)
            values['output_' + output['content']] = '${output_' + c['content'] + '}'
        html = Template(imported_document['html']).safe_substitute(**values)
        model.Document(
            _owner=imported_document['_owner'],
            _category=ObjectId(workspace),
            title=imported_document['title'],
            content=content,
            public=imported_document['public'],
            visible=imported_document['visible'],
            html=html
        )
        model.DBSession.flush_all()
        tg.flash('Document successfully imported!')
        return redirect(tg.url('/document', params=dict(workspace=workspace)))


def import_qa(imported_document, qa_id, owner, workspace_id):
    qa = imported_document['qa'][qa_id]

    prec_id = import_precondition(imported_document, qa['_parent_precondition'], owner, workspace_id) \
        if qa['_parent_precondition'] else None

    if qa:
        inserted = upsert_document(model_class=model.Qa, _owner=ObjectId(owner),
                             _category=ObjectId(workspace_id),
                             _parent_precondition=prec_id,
                             title=qa['title'],
                             question=qa['question'],
                             tooltip=qa['tooltip'],
                             link=qa['link'],
                             type=qa['type'],
                             answers=qa['answers'],
                             public=qa['public'],
                             visible=qa['visible'])
        return inserted._id


def import_precondition(imported_document, precondition_id, owner, workspace_id):
    if precondition_id in ['and', 'or', '(', ')', 'not']:
        return precondition_id

    s_preconditions, a_preconditions = imported_document['simple_preconditions'], imported_document[
        'advanced_preconditions']

    if precondition_id in s_preconditions:
        precondition = s_preconditions[str(precondition_id)]
        qa_id = import_qa(imported_document, precondition['condition'][0], owner, workspace_id)
        condition = [ObjectId(qa_id), precondition['condition'][1]]
    elif precondition_id in a_preconditions:
        precondition = a_preconditions[str(precondition_id)]
        condition = [import_precondition(imported_document, condition, owner, workspace_id) for condition in
                     precondition['condition']]

    prec = upsert_document(model_class=model.Precondition, _owner=ObjectId(owner),
                           _category=ObjectId(workspace_id),
                           title=precondition['title'],
                           type=precondition['type'],
                           condition=condition)
    return prec._id


def upsert_document(model_class, **body):
    fetched = model_class.query.find(body).first()
    if fetched:
        return fetched
    inserted = model_class(**body)
    model.DBSession.flush_all()
    return inserted


def import_output(imported_document, output_id, owner, workspace_id):
    output = imported_document['outputs'][output_id]
    prec_id = import_precondition(imported_document, output['_precondition'], owner, workspace_id)
    content = []
    values ={}
    for element in output['content']:
        c = {'type': element['type'], 'title': element['title']}
        if element['type'] == 'output':
            c['content'] = str(import_output(imported_document, element['content'], owner, workspace_id))
            values['output_' + element['content']] = '${output_' + c['content'] + '}'
        elif element['type'] == 'qa_response':
            c['content'] = str(import_qa(imported_document, element['content'], owner, workspace_id))
            values['qa_' + element['content']] = '${qa_' + c['content']+'}'
        content.append(c)

    html = Template(output['html']).safe_substitute(**values)

    output_inserted = upsert_document(model_class=model.Output,
                                      title=output['title'],
                                      _category=ObjectId(workspace_id),
                                      _owner=ObjectId(owner),
                                      html=html,
                                      _precondition=ObjectId(prec_id),
                                      public=output['public'],
                                      visible=output['visible'],
                                      content=content)
    return output_inserted._id


def export_outputs(output_id, document):
    o = model.Output.query.get(_id=ObjectId(output_id)).__json__()
    o.pop('created_at', None)
    o.pop('_category', None)
    o.pop('_owner', None)
    o.pop('entity', None)
    if o['_id'] not in document['outputs']:
        document['outputs'][str(o['_id'])] = o
        export_preconditions(o['_precondition'], document)
    for content in o['content']:
        if content['type'] == 'output':
            export_outputs(content['content'], document)
        elif content['type'] == 'qa_response':
            export_qa(content['content'], document)


def export_qa(qa_id, document):
    qa = model.Qa.query.get(_id=ObjectId(qa_id)).__json__()
    qa.pop('_category', None)
    qa.pop('_owner', None)
    qa.pop('entity', None)
    if qa['_id'] not in document['qa']:
        document['qa'][str(qa['_id'])] = qa
        if qa['_parent_precondition']:
            export_preconditions(qa['_parent_precondition'], document)


def export_preconditions(precondition_id, document):
    if precondition_id in ['and', 'or', '(', ')', 'not']:
        return
    precondition = model.Precondition.query.get(_id=ObjectId(precondition_id)).__json__()
    precondition.pop('_owner', None)
    precondition.pop('_category', None)
    precondition.pop('entity', None)

    if precondition['type'] == 'simple':
        if precondition['_id'] not in document['simple_preconditions']:
            document['simple_preconditions'][str(precondition['_id'])] = precondition
            export_qa(precondition['condition'][0], document)
    elif precondition['type'] == 'advanced':
        for condition in precondition['condition']:
            export_preconditions(condition, document)
        if precondition['_id'] not in document['advanced_preconditions']:
            document['advanced_preconditions'][str(precondition['_id'])] = precondition
