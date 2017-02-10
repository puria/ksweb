# -*- coding: utf-8 -*-
from string import Template

from bson import ObjectId
import ming


def to_object_id(s):
    if not s:
        return None
    return ObjectId(s)


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
    for c in obj.content:
        if c['type'] == 'output':
            values['output_' + c['content']] = editor_widget_template_for_output(id_=c['content'], title=c['title'])
        else:
            # qa_response
            values['qa_' + c['content']] = editor_widget_template_for_qa(id_=c['content'], title=c['title'])

    return Template(obj.html).safe_substitute(**values)








