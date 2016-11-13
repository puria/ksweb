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


def clone_obj(class_, original_obj, values):

    print "old values", to_dict(original_obj)
    print "values", values

    for k, v in to_dict(original_obj).items():
        if k not in values:
            values[k] = v

    values.pop('entity', None)
    values.pop('_id', None)

    return class_(**values)











