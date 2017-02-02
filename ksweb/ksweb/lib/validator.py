# -*- coding: utf-8 -*-
import HTMLParser
import ast
import json

from bson import ObjectId
from bson.errors import InvalidId
from tw2.core import ListLengthValidator
from tw2.core import Validator, ValidationError
from tg.i18n import lazy_ugettext as l_

from ksweb import model


class QAExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            qa = model.Qa.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(l_(u'Domanda non esistente'), self)

        if qa is None:
            raise ValidationError(l_(u'Domanda non esistente'), self)


class CategoryExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            category = model.Category.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(l_(u'Categoria non esistente'), self)

        if category is None:
            raise ValidationError(l_(u'Categoria non esistente'), self)


class PreconditionExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            precondition = model.Precondition.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(l_(u'Filtro non esistente'), self)

        if precondition is None:
            raise ValidationError(l_(u'Filtro non esistente'), self)


class OutputExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            output = model.Output.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(l_(u'Output non esistente'), self)

        if output is None:
            raise ValidationError(l_(u'Output non esistente'), self)


class DocumentExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            document = model.Document.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(l_(u'Documento non esistente'), self)

        if document is None:
            raise ValidationError(l_(u'Documento non esistente'), self)


class QuestionaryExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            questionary = model.Questionary.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(l_(u'Questionario non esistente'), self)

        if questionary is None:
            raise ValidationError(l_(u'Questionario non esistente'), self)


class OutputContentValidator(ListLengthValidator):
    def _validate_python(self, value, state=None):
        document_accepted_type = ['qa_response', 'output']
        for cond in value:
            if cond['type'] == 'qa_response':
                qa = model.Qa.query.get(_id=ObjectId(cond['content']))
                if not qa:
                    raise ValidationError(l_(u'Domanda non trovata.'), self)
            elif cond['type'] == 'output':
                out = model.Output.query.get(_id=ObjectId(cond['content']))
                if not out:
                    raise ValidationError(l_(u'Output non trovato'), self)
            else:
                raise ValidationError(l_(u'Condizione non valida.'), self)

    def _convert_to_python(self, value, state=None):
        if isinstance(value, basestring):
            # need transform from string to list
            return ast.literal_eval(value)
        return value


class ConditionValidator(Validator):

    def _validate_python(self, value, state=None):
        super(ConditionValidator, self)._validate_python(value, state)

    def _convert_to_python(self, value, state=None):
        try:
            value = json.loads(value)
        except Exception as e:
            raise ValidationError(l_(u'Condizione non valida.'), self)

        for index, v in enumerate(value):
            try:
                value[index] = ObjectId(v)
            except InvalidId:
                continue
        return value


class AnswersValidator(Validator):

    def _validate_python(self, value, state=None):
        super(AnswersValidator, self)._validate_python(value, state)

    def _convert_to_python(self, value, state=None):
        try:
            value = json.loads(value)
        except Exception as e:
            raise ValidationError(l_(u'Condizione non valida.'), self)

        return value

class DocumentContentValidator(Validator):
    def _validate_python(self, value, state=None):
        document_accepted_type = ['text', 'output']
        for cond in value:
            if cond['type'] == 'text':
                cond['content'] = HTMLParser.HTMLParser().unescape(cond['content'])
            elif cond['type'] == 'output':
                output = model.Output.query.get(_id=ObjectId(cond['content']))
                if not output:
                    raise ValidationError(l_(u'Output non trovato.'), self)
            else:
                raise ValidationError(l_(u'Condizione non valida.'), self)