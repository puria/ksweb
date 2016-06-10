from ksweb.tests import TestController
from ksweb.lib.validator import CategoryExistValidator, QAExistValidator
from tw2.core import ValidationError


class TestValidators(TestController):
    application_under_test = 'main'

    def test_qa_exist_validator(self):
        self._login_lavewr()
        category1 = self._get_category('Category_1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'], qa_params['link'], qa_params['answer_type'], qa_params['answers'])

        qa = self._get_qa(qa_params['title'])
        validator = QAExistValidator()
        try:
            res = validator._validate_python(str(qa._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_qa_exist_validator_with_obj_not_valid(self):
        validator = QAExistValidator()
        try:
            res = validator._validate_python('not_obj_id')
        except ValidationError:
            assert True
        else:
            assert False

    def test_qa_exist_validator_with_not_existing_qa(self):
        validator = QAExistValidator()
        try:
            res = validator._validate_python('5757ce79c42d752bde919318')
        except ValidationError:
            assert True
        else:
            assert False

    def test_category_exist_validator(self):
        category1 = self._get_category('Category_1')
        validator = CategoryExistValidator()
        try:
            res = validator._validate_python(str(category1._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_category_exist_validator_with_obj_not_valid(self):
        validator = CategoryExistValidator()
        try:
            res = validator._validate_python('not_obj_id')
        except ValidationError:
            assert True
        else:
            assert False

    def test_category_exist_validator_with_not_existing_category(self):
        validator = CategoryExistValidator()
        try:
            res = validator._validate_python('5757ce79c42d752bde919318')
        except ValidationError:
            assert True
        else:
            assert False
