# -*- coding: utf-8 -*-
"""Unit and functional test suite for ksweb."""

from os import getcwd

from bson import ObjectId
from paste.deploy import loadapp
from webtest import TestApp
from gearbox.commands.setup_app import SetupAppCommand
from tg import config
from tg.util import Bunch

from ksweb import model
from ksweb.model import DBSession

__all__ = ['setup_app', 'setup_db', 'teardown_db', 'TestController']

application_name = 'main_without_authn'


def load_app(name=application_name):
    """Load the test application."""
    return TestApp(loadapp('config:test.ini#%s' % name, relative_to=getcwd()))


def setup_app():
    """Setup the application."""
    cmd = SetupAppCommand(Bunch(options=Bunch(verbose_level=1)), Bunch())
    cmd.run(Bunch(config_file='config:test.ini', section_name=None))


def setup_db():
    """Create the database schema (not needed when you run setup_app)."""
    datastore = config['tg.app_globals'].ming_datastore
    model.init_model(datastore)


def teardown_db():
    """Destroy the database schema."""
    datastore = config['tg.app_globals'].ming_datastore
    try:
        # On MIM drop all data
        datastore.conn.drop_all()
    except TypeError:
        # On MongoDB drop database
        datastore.conn.drop_database(datastore.db)


class TestController(object):
    FAKE_RESPONSE = ['Resp1', 'Resp2', 'Resp3']

    """Base functional test case for the controllers.

    The ksweb application instance (``self.app``) set up in this test
    case (and descendants) has authentication disabled, so that developers can
    test the protected areas independently of the :mod:`repoze.who` plugins
    used initially. This way, authentication can be tested once and separately.

    Check ksweb.tests.functional.test_authentication for the repoze.who
    integration tests.

    This is the officially supported way to test protected areas with
    repoze.who-testutil (http://code.gustavonarea.net/repoze.who-testutil/).

    """
    application_under_test = application_name

    def setUp(self):
        """Setup test fixture for each functional test method."""
        self.app = load_app(self.application_under_test)
        setup_app()

    def tearDown(self):
        """Tear down test fixture for each functional test method."""
        teardown_db()

    def _login_admin(self):
        self.app.get(
            '/login_handler?login=admin&password=adminks', status=302
        )

    def _login_lavewr(self):
        self.app.get('/login_handler?login=lawyer&password=lawyerks', status=302)

    def _get_user(self, email_address):
        return model.User.query.get(email_address=email_address)

    #  Rewrite utility method for test
    #  Category Utility
    def _get_category(self, name):
        return model.Category.query.get(name=name)

    def _create_category(self, name, visible=True):
        c = model.Category(
                name=name,
                visible=visible
        )
        DBSession.flush(c)
        return c

    def _get_or_create_category(self, name, visible=True):
        c = self._get_category(name)
        if c:
            return c
        return self._create_category(name, visible)

    #  Question And Answer Utility
    def _get_qa(self, id):
        return model.Qa.query.get(_id=ObjectId(id))

    def _get_qa_by_title(self, title):
        return model.Qa.query.get(title=title)

    def _create_qa(self, title, category_id, question, tooltip, link, qa_type, answers):
        self.app.post_json(
            '/qa/post', params={
                'title': title,
                'category': str(category_id),
                'question': question,
                'tooltip': tooltip,
                'link': link,
                'answer_type': qa_type,
                'answers': answers
            }
        )
        return self._get_qa_by_title(title)

    def _get_or_create_qa(self, title, category_id=None, question=None, tooltip=None, link=None, qa_type=None, answers=None):
        qa = self._get_qa_by_title(title)
        if qa:
            return qa

        return self._create_qa(title, category_id, question, tooltip, link, qa_type, answers)

    def _create_fake_qa(self, title, qa_type='single', answers=FAKE_RESPONSE):
        fake_category = self._get_or_create_category('fake_category')
        return self._create_qa(
            title,
            fake_category._id,
            '%s_fake_question' % title,
            'fake_tooltip_%s' % title,
            'fake_link_%s' % title,
            qa_type,
            answers
        )

    #  Precondition utility
    def _get_precond(self, id):
        return model.Precondition.query.get(title=ObjectId(id))

    def _get_precond_by_title(self, title):
        return model.Precondition.query.get(title=title)

    def _create_simple_precondition(self, title, category_id, qa_id, answer_type='what_response', interested_response=[]):
        """
        answer_type = ['have_response', what_response]
        """
        self.app.post_json(
            '/precondition/simple/post', params={
                'title': title,
                'category': str(category_id),
                'question': str(qa_id),
                'answer_type': answer_type,
                'interested_response': interested_response
            }
        )
        return self._get_precond_by_title(title)

    def _create_fake_simple_precondition(self, title, category_id=None):
        if not category_id:
            category_id = self._get_or_create_category("Fake_cat_%s" % title)._id

        return self._create_simple_precondition(title, category_id, self._create_fake_qa(title)._id, 'what_response', [self.FAKE_RESPONSE[0]])

    def _create_advanced_precondition(self, title, category_id, conditions=[]):
        self.app.post_json(
            '/precondition/advanced/post', params={
                'title': title,
                'category': str(category_id),
                'conditions': conditions
            }
        )
        return self._get_precond_by_title(title)

    #  Output Utility
    def _get_output(self, id):
        return model.Output.query.get(_id=ObjectId(id))

    def _get_output_by_title(self, title):
        return model.Output.query.get(title=title)

    def _create_output(self, title, category_id, precondition_id, content):
        if isinstance(content, (str, unicode)):
            content = [{
                'type': "text",
                'content': content,
                'title': ""
                }]

        self.app.post_json(
            '/output/post', params={
                'title': title,
                'content': content,
                'category': str(category_id),
                'precondition': str(precondition_id)
            }
        )
        return self._get_output_by_title(title)

    def _create_fake_output(self, title, category_id=None):
        if not category_id:
            category_id = self._get_or_create_category("Fake_cat_%s" % title)._id
        return self._create_output(title, category_id, self._create_fake_simple_precondition(title)._id, "Fake content text")

    #  Document Utility

    def _get_document_by_title(self, title):
        return model.Document.query.get(title=title)