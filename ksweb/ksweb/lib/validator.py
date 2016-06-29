# -*- coding: utf-8 -*-
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


class OutputContentValidator(Validator):
    def _validate_python(self, value, state=None):
        document_accepted_type = ['text', 'qa_response']
        for cond in value:
            if cond['type'] not in document_accepted_type:
                raise ValidationError(u'Condizione non valida.', self)

            if cond['type'] == 'qa_response':
                qa = model.Qa.query.get(_id=ObjectId(cond['content']))
                if not qa:
                    raise ValidationError(u'Domanda non trovata.', self)


class DocumentContentValidator(Validator):
    def _validate_python(self, value, state=None):
        document_accepted_type = ['text', 'output']
        for cond in value:
            if cond['type'] not in document_accepted_type:
                raise ValidationError(u'Condizione non valida.', self)

            if cond['type'] == 'output':
                output = model.Output.query.get(_id=ObjectId(cond['content']))
                if not output:
                    raise ValidationError(u'Output non trovato.', self)
