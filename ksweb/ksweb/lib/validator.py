from bson import ObjectId
from tw2.core import Validator, ValidationError

from ksweb import model


class CategoryExistValidator(Validator):
    def _validate_python(self, value, state=None):
        category = model.Category.query.get(_id=ObjectId(value))
        if category is None:
            raise ValidationError(u'Categoria non esistente', self)
