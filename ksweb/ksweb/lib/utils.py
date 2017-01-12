# -*- coding: utf-8 -*-

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
            flash(u'La sessione per la modifica dell\'oggetto è scaduta o non esiste', 'warning')
            return redirect(base_url='/')
        return func(*args, **kw)
    return wrapper










