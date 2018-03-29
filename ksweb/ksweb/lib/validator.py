# -*- coding: utf-8 -*-
try:
    import HTMLParser
except ImportError:
    from html.parser import HTMLParser
import ast

from bson import ObjectId
from bson.errors import InvalidId
from tw2.core import ListLengthValidator
from tw2.core import Validator, ValidationError
from tg.i18n import lazy_ugettext as l_

from ksweb import model

try:
    basestring
except NameError:
    basestring = str

class EntityValidator(Validator):
    entity = None
    msgs = {
        'not_exists': l_('Value is too short'),
    }

    def _validate_python(self, value, state=None):
        try:
            found = self.entity.query.get(_id=ObjectId(value))
        except (InvalidId, TypeError):
            raise ValidationError('not_exists', self)

        if found is None:
            raise ValidationError('not_exists', self)


class QAExistValidator(EntityValidator):
    entity = model.Qa
    msgs = dict(not_exists=l_(u'Question does not exists'))


class WorkspaceExistValidator(EntityValidator):
    entity = model.Category
    msgs = dict(not_exists=l_(u'Work Area does not exists'))


class PreconditionExistValidator(EntityValidator):
    entity = model.Precondition
    msgs = dict(not_exists=l_(u'Filter does not exists'))


class OutputExistValidator(EntityValidator):
    entity = model.Output
    msgs = dict(not_exists=l_(u'Output does not exists'))


class DocumentExistValidator(EntityValidator):
    entity = model.Document
    msgs = dict(not_exists=l_(u'Document does not exists'))


class QuestionaryExistValidator(EntityValidator):
    entity = model.Questionary
    msgs = dict(not_exists=l_(u'Questionary does not exists'))


class OutputContentValidator(ListLengthValidator):
    def _validate_python(self, value, state=None):
        for cond in value:
            if cond['type'] == 'qa_response':
                qa = model.Qa.query.get(_id=ObjectId(cond['content']))
                if not qa:
                    raise ValidationError(l_(u'Question not found.'), self)
            elif cond['type'] == 'output':
                out = model.Output.query.get(_id=ObjectId(cond['content']))
                if not out:
                    raise ValidationError(l_(u'Output not found'), self)
            else:
                raise ValidationError(l_(u'Invalid Filter.'), self)

    def _convert_to_python(self, value, state=None):
        if isinstance(value, basestring):
            # need transform from string to list
            return ast.literal_eval(value)
        return value


class DocumentContentValidator(Validator):
    def _validate_python(self, value, state=None):
        document_accepted_type = ['output']
        for cond in value:
            if cond['type'] == 'output':
                output = model.Output.query.get(_id=ObjectId(cond['content']))
                if not output:
                    raise ValidationError(l_(u'Output not found.'), self)
            else:
                raise ValidationError(l_(u'Invalid Filter.'), self)
