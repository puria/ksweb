# -*- coding: utf-8 -*-
from string import Template

from bson import ObjectId
import ming
from ksweb import model


def to_object_id(s):
    return ObjectId(s) if s else None


def to_dict(obj):
    """Converts a Ming model to a dictionary"""
    prop_names = [
        prop.name for prop in ming.odm.mapper(obj).properties if isinstance(prop, ming.odm.property.FieldProperty)
    ]
    props = {}
    for key in prop_names:
        props[key] = getattr(obj, key)
    return props


def clone_obj(class_, original_obj, params):
    values = params.copy()

    for k, v in to_dict(original_obj).items():
        if k not in values:
            values[k] = v

    values.pop('entity', None)
    values.pop('_id', None)

    return class_(**values)


# use as decorator
def with_entity_session(func):
    def wrapper(*args, **kw):
        from tg import session, flash, redirect
        if not session.get('entity'):
            flash(u'Editing Session expired or invalid', 'warning')
            return redirect(base_url='/')
        return func(*args, **kw)
    return wrapper


def _upcast(obj):
    from ksweb.lib.helpers import editor_widget_template_for_output, editor_widget_template_for_qa

    values = dict()

    # qa_response and output only
    if obj.content:
        for c in obj.content:
            if c['type'] == 'output':
                values['output_' + c['content']] = editor_widget_template_for_output(id_=c['content'], title=c['title'])
            else:
                # qa_response
                values['qa_' + c['content']] = editor_widget_template_for_qa(id_=c['content'], title=c['title'])

    return Template(obj.html).safe_substitute(**values)


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

    s_preconditions, a_preconditions = imported_document['simple_preconditions'], imported_document['advanced_preconditions']

    if precondition_id in s_preconditions:
        precondition = s_preconditions[str(precondition_id)]
        qa_id = import_qa(imported_document, precondition['condition'][0], owner, workspace_id)
        condition = [ObjectId(qa_id), precondition['condition'][1]]
    elif precondition_id in a_preconditions:
        precondition = a_preconditions[str(precondition_id)]
        condition = [import_precondition(imported_document, condition, owner, workspace_id) for condition in precondition['condition']]
    else:
        return

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
    precondition = model.Precondition.query.get(_id=ObjectId(precondition_id))
    if not precondition: return
    precondition = precondition.__json__()
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

def get_related_entities_for_filters(_id):
    outputs_related = model.Output.query.find({'_precondition': ObjectId(_id)}).all()
    preconditions_related = model.Precondition.query.find(
        {'type': 'advanced', 'condition': ObjectId(_id)}).all()
    qas_related = model.Qa.query.find({"_parent_precondition": ObjectId(_id)}).all()

    entities = list(outputs_related + preconditions_related + qas_related)

    return {
        'entities': entities,
        'len': len(entities)
    }




