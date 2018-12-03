# -*- coding: utf-8 -*-
from ksweb.lib.utils import get_entities_from_str
from tg.validation import TGValidationError

try:
    import HTMLParser
except ImportError:
    from html.parser import HTMLParser

from bson.errors import InvalidId
from tw2.core import Validator, ValidationError
from tg.i18n import lazy_ugettext as l_

from ksweb import model


class EntityValidator(Validator):
    entity = None
    msgs = {
        'not_exists': l_('Value is too short'),
    }

    def _validate_python(self, value, state=None):
        try:
            found = self.entity.by_id(value)
        except InvalidId:
            found = self.entity.by_hash(value)

        if found is None:
            raise ValidationError('not_exists', self)


class QAExistValidator(EntityValidator):
    entity = model.Qa
    msgs = dict(not_exists=l_(u'Question does not exists'))


class WorkspaceExistValidator(EntityValidator):
    entity = model.Workspace
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


class OutputContentValidator(Validator):
    def _validate_python(self, value, state=None):
        outputs, answers = get_entities_from_str(value)
        if None in outputs:
            raise ValidationError(l_(u'Output not found.'), self)
        if None in answers:
            raise ValidationError(l_(u'Question not found.'), self)


class DocumentContentValidator(Validator):
    def _validate_python(self, value, state=None):
        outputs, __ = get_entities_from_str(value)
        if None in outputs:
            raise ValidationError(l_(u'Output not found.'), self)
