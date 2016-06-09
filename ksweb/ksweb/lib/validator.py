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
