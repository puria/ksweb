from ksweb import model
from ksweb.model import DBSession
from ksweb.tests import TestController
from ksweb.lib.validator import CategoryExistValidator, QAExistValidator, DocumentExistValidator, \
    PreconditionExistValidator, DocumentContentValidator, OutputExistValidator, OutputContentValidator, \
    QuestionaryExistValidator
from tg.util.webtest import test_context
from tw2.core import ValidationError
from test_document import TestDocument


class TestValidators(TestController):
    application_under_test = 'main'

    def test_qa_exist_validator(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        qa_params = {
            'title': 'Title of QA',
            'category': str(category1._id),
            'question': 'Text of the question',
            'tooltip': 'Tooltip of QA1',
            'link': 'http://www.axant.it',
            'answer_type': 'single',
            'answers': ['Risposta1', 'Risposta2', 'Risposta3']
        }
        qa = self._create_qa(qa_params['title'], qa_params['category'], qa_params['question'], qa_params['tooltip'], qa_params['link'], qa_params['answer_type'], qa_params['answers'])

        validator = QAExistValidator()
        try:
            res = validator._validate_python(str(qa._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_qa_exist_validator_with_obj_not_valid(self):
        with test_context(self.app):
            validator = QAExistValidator()
            try:
                res = validator._validate_python('not_obj_id')
            except ValidationError:
                assert True
            else:
                assert False

    def test_qa_exist_validator_with_not_existing_qa(self):
        with test_context(self.app):
            validator = QAExistValidator()
            try:
                res = validator._validate_python('5757ce79c42d752bde919318')
            except ValidationError:
                assert True
            else:
                assert False

    def test_category_exist_validator(self):
        category1 = self._get_category('Area 1')
        validator = CategoryExistValidator()
        try:
            res = validator._validate_python(str(category1._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_category_exist_validator_with_obj_not_valid(self):
        with test_context(self.app):
            validator = CategoryExistValidator()
            try:
                res = validator._validate_python('not_obj_id')
            except ValidationError:
                assert True
            else:
                assert False

    def test_category_exist_validator_with_not_existing_category(self):
        with test_context(self.app):
            validator = CategoryExistValidator()
            try:
                res = validator._validate_python('5757ce79c42d752bde919318')
            except ValidationError:
                assert True
            else:
                assert False

    def test_document_exist_validator(self):
        model.Document(
            _owner=self._get_user('lawyer1@ks.axantweb.com')._id,
            _category=self._get_category('Area 1')._id,
            title="Titolone",
            html='',
            content=[],
            public=True,
            visible=True
        )
        DBSession.flush()
        document = model.Document.query.get(title="Titolone")
        validator = DocumentExistValidator()
        try:
            res = validator._validate_python(str(document._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_document_not_exist_validator(self):
        with test_context(self.app):
            validator = DocumentExistValidator()
            try:
                res = validator._validate_python("5757ce79c42d752bde919318")
            except ValidationError:
                assert True
            else:
                assert False

    def test_document_invalid_id_validator(self):
        with test_context(self.app):
            validator = DocumentExistValidator()
            try:
                res = validator._validate_python("Invalid")
            except ValidationError:
                assert True
            else:
                assert False

    def test_precondition_exist_invalid_id_validator(self):
        with test_context(self.app):
            validator = PreconditionExistValidator()
            try:
                res = validator._validate_python("Invalid")
            except ValidationError:
                assert True
            else:
                assert False

    def test_output_exist_validator(self):
        model.Output(
            title="Fake_output",
            content=[],
            html='',
            _owner=self._get_user('lawyer1@ks.axantweb.com')._id,
            _category=self._get_category('Area 1')._id,
            _precondition=None
        )
        DBSession.flush()
        output = model.Output.query.get(title="Fake_output")
        validator = OutputExistValidator()
        try:
            res = validator._validate_python(str(output._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_output_not_exist_validator(self):
        with test_context(self.app):
            validator = OutputExistValidator()
            try:
                res = validator._validate_python("5757ce79c42d752bde919318")
            except ValidationError:
                assert True
            else:
                assert False

    def test_output_invalid_id_validator(self):
        with test_context(self.app):
            validator = OutputExistValidator()
            try:
                res = validator._validate_python("Invalid")
            except ValidationError:
                assert True
            else:
                assert False

    def test_output_content_validator(self):
        self._login_lawyer()
        qa1 = self._create_qa('FakeQa1', self._get_category('Area 1')._id, 'Di che sesso sei', 'tooltip', 'link',
                              'text', '')

        with test_context(self.app):

            validator = OutputContentValidator()
            try:
                res = validator._validate_python([
                    {
                        'type': "qa_response",
                        'content': str(qa1._id),
                        'title': qa1.title
                    },
                ])
            except ValidationError:
                assert False
            else:
                assert True

    def test_output_content_validator_invalid_output(self):
        with test_context(self.app):
            validator = OutputContentValidator()
            try:
                res = validator._validate_python([
                    {
                        'type': "text",
                        'content': "Buongiorno",
                        'title': ""
                    },
                    {
                        'type': "qa_response",
                        'content': "5757ce79c42d752bde919318",
                        'title': "fake title"
                    },
                ])
            except ValidationError:
                assert True
            else:
                assert False

    def test_output_content_validator_invalid_type_output(self):
        with test_context(self.app):
            validator = OutputContentValidator()
            try:
                res = validator._validate_python([
                    {
                        'type': "fake_type",
                        'content': "Buongiorno",
                        'title': ""
                    }
                ])
            except ValidationError:
                assert True
            else:
                assert False

    def test_document_content_validator(self):
        with test_context(self.app):
            model.Output(
                title="FakeOutput",
                content="Content of the fake output",
                html='',
                _owner=self._get_user('lawyer1@ks.axantweb.com')._id,
                _category=self._get_category('Area 1')._id,
                _precondition=None,
            )
            DBSession.flush()
            output = model.Output.query.get(title="FakeOutput")

            validator = DocumentContentValidator()
            try:
                res = validator._validate_python([
                    {
                        'type': "output",
                        'content': str(output._id),
                        'title': output.title
                    },
                ])
            except ValidationError:
                assert False
            else:
                assert True

    def test_document_content_validator_invalid_output(self):
        with test_context(self.app):
            validator = DocumentContentValidator()
            try:
                res = validator._validate_python([
                    {
                        'type': "text",
                        'content': "Buongiorno",
                        'title': ""
                    },
                    {
                        'type': "output",
                        'content': "5757ce79c42d752bde919318",
                        'title': "fake title"
                    },
                ])
            except ValidationError:
                assert True
            else:
                assert False

    def test_document_content_validator_invalid_type_output(self):
        with test_context(self.app):
            validator = DocumentContentValidator()
            try:
                res = validator._validate_python([
                    {
                        'type': "fake_type",
                        'content': "Buongiorno",
                        'title': ""
                    }
                ])
            except ValidationError:
                assert True
            else:
                assert False

    def test_questionary_exist_validator(self):
        self._login_lawyer()
        fake_questionary = self._create_fake_questionary('Test_validator')
        validator = QuestionaryExistValidator()
        try:
            res = validator._validate_python(str(fake_questionary._id))
        except ValidationError:
            assert False
        else:
            assert True

    def test_questionary_not_exist_validator(self):
        with test_context(self.app):
            validator = QuestionaryExistValidator()
            try:
                res = validator._validate_python("5757ce79c42d752bde919318")
            except ValidationError:
                assert True
            else:
                assert False

    def test_questionary_invalid_id_validator(self):
        with test_context(self.app):
            validator = QuestionaryExistValidator()
            try:
                res = validator._validate_python("Invalid")
            except ValidationError:
                assert True
            else:
                assert False
