# -*- coding: utf-8 -*-
import HTMLParser
import ast
import json

from bson import ObjectId
from bson.errors import InvalidId
from tw2.core import Validator, ValidationError

from ksweb import model


class QAExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            qa = model.Qa.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(u'Domanda non esistente', self)

        if qa is None:
            raise ValidationError(u'Domanda non esistente', self)


class CategoryExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            category = model.Category.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(u'Categoria non esistente', self)

        if category is None:
            raise ValidationError(u'Categoria non esistente', self)


class PreconditionExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            precondition = model.Precondition.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(u'Precondizione non esistente', self)

        if precondition is None:
            raise ValidationError(u'Precondizione non esistente', self)


class OutputExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            output = model.Output.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(u'Output non esistente', self)

        if output is None:
            raise ValidationError(u'Output non esistente', self)


class DocumentExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            document = model.Document.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(u'Documento non esistente', self)

        if document is None:
            raise ValidationError(u'Documento non esistente', self)


class QuestionaryExistValidator(Validator):
    def _validate_python(self, value, state=None):

        try:
            questionary = model.Questionary.query.get(_id=ObjectId(value))
        except InvalidId:
            raise ValidationError(u'Questionario non esistente', self)

        if questionary is None:
            raise ValidationError(u'Questionario non esistente', self)


class OutputContentValidator(Validator):
    def _validate_python(self, value, state=None):
        document_accepted_type = ['text', 'qa_response','output']
        for cond in value:
            if cond['type'] == 'text':
                cond['content'] = HTMLParser.HTMLParser().unescape(cond['content'])
            elif cond['type'] == 'qa_response':
                qa = model.Qa.query.get(_id=ObjectId(cond['content']))
                if not qa:
                    raise ValidationError(u'Domanda non trovata.', self)
            elif cond['type'] == 'output':
                out = model.Output.query.get(_id=ObjectId(cond['content']))
                if not out:
                    raise ValidationError(u'Output non trovato', self)
            else:
                raise ValidationError(u'Condizione non valida.', self)

    def _convert_to_python(self, value, state=None):
        if isinstance(value, basestring):
            # need transform from string to list
            return ast.literal_eval(value)
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
                    raise ValidationError(u'Output non trovato.', self)
            else:
                raise ValidationError(u'Condizione non valida.', self)