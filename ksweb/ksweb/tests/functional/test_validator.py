from ksweb.tests import TestController
from ksweb.lib.validator import CategoryExistValidator
from tw2.core import ValidationError


class TestValidators(TestController):

    def test_category_exist_validator(self):
        category1 = self._get_category('Category_1')
        validator = CategoryExistValidator()
        try:
            res = validator._validate_python(str(category1._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_category_exist_validator_with_error(self):
        validator = CategoryExistValidator()
        try:
            res = validator._validate_python('not_obj_id')
        except ValidationError:
            assert True
        else:
            assert False
