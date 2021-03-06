# -*- coding: utf-8 -*-
from string import Template
from bson import ObjectId
from bson.errors import InvalidId
from ksweb.model import Output, Precondition, Qa, Document
from markupsafe import Markup
from tg.util.ming import dictify
from ksweb import model


# https://stackoverflow.com/questions/34360603/python-template-safe-substitution-with-the-custom-double-braces-format
class TemplateOutput(Template):
    delimiter = '#'


class TemplateAnswer(Template):
    delimiter = '@'


def find_entities_from_html(html):
    if not html:
        return [], []
    import re
    outputs_hashes = re.findall(r'#{([^\W]+)\b}', html)
    answers_hashes = re.findall(r'@{([^\W]+)\b}', html)
    return outputs_hashes, answers_hashes


def to_object_id(s):
    return ObjectId(s) if s else None


def five_words(html):
    return " ".join(Markup(html).striptags().split()[:5])


def clone_obj(class_, original_obj, params):
    items = dictify(original_obj).items()
    cloned = {k: v for k, v in items if k not in params.keys()}
    cloned.update(params)
    cloned.pop('entity', None)
    cloned.pop('_id', None)
    return class_(**cloned)


# use as decorator
def with_entity_session(func):
    def wrapper(*args, **kw):
        from tg import session, flash, redirect
        if not session.get('entity'):
            flash(u'Editing Session expired or invalid', 'warning')
            return redirect(base_url='/')
        return func(*args, **kw)
    return wrapper


def upsert_document(cls, **body):
    fetched = cls.query.find(body).first()
    if fetched:
        return fetched
    inserted = cls(**body)
    return inserted


def get_related_entities_for_filters(_id):
    outputs_related = model.Output.query.find({'_precondition': ObjectId(_id)}).all()
    preconditions_related = model.Precondition.query.find({'type': 'advanced', 'condition': ObjectId(_id)}).all()
    qas_related = model.Qa.query.find({"_parent_precondition": ObjectId(_id)}).all()
    entities = list(outputs_related + preconditions_related + qas_related)
    return dict(entities=entities, len=len(entities))


def get_entities_from_str(html):
    outputs_ids, answers_ids = find_entities_from_html(html)
    outputs = [model.Output.query.get(hash=__) for __ in outputs_ids]
    answers = [model.Qa.query.get(hash=__) for __ in answers_ids]
    return outputs, answers


def entity_from_hash(hash):
    output = Output.query.get(hash=hash)
    precondition = Precondition.query.get(hash=hash)
    qa = Qa.query.get(hash=hash)
    document = Document.query.get(hash=hash)
    entity = list(filter(None, [output, precondition, qa, document]))
    if len(entity):
        return entity[0]

    return None


def entity_from_id(_id):
    try:
        oid = ObjectId(_id)
    except InvalidId:
        return None
    output = Output.query.get(_id=oid)
    precondition = Precondition.query.get(_id=oid)
    qa = Qa.query.get(_id=oid)
    document = Document.query.get(_id=oid)
    entity = list(filter(None, [output, precondition, qa, document]))
    if len(entity):
        return entity[0]

    return None


def hash_to_id(_hash, cls):
    me = cls.query.get(hash=_hash)
    return str(me._id) if me else _hash


def id_to_hash(_id, cls):
    try:
        me = cls.query.get(ObjectId(_id))
    except InvalidId:
        return _id
    return me.hash if me else _id


def ksweb_error_handler(*args, **kw):  # pragma: nocover
    from tg import flash, redirect
    from tg._compat import unicode_text
    from tg.request_local import request
    from tg.i18n import lazy_ugettext as l_
    _request = request._current_obj()
    errors = dict(
        (unicode_text(key), unicode_text(error)) for key, error in _request.validation.errors.items()
    )
    flash(l_('Errors: %s' % errors), 'error')
    redirect('/start')


def uid():
    from tg import request
    return request.identity['user']._id


def save_to_session():
    pass
