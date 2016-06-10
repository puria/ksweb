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

    def _get_category(self, category_name):
        return model.Category.query.get(name=category_name)

    def _create_qa(self, title, category_id, question, tooltip, link, type, answers):
        self.app.post_json(
            '/qa/post', params={
                'title': title,
                'category': str(category_id),
                'question': question,
                'tooltip': tooltip,
                'link': link,
                'answer_type': type,
                'answers': answers
            }
        )

    def _create_output(self, title, category, precondition, content):
        self.app.post_json(
            '/output/post', params={
                'title': title,
                'content': content,
                'category': str(category._id),
                'precondition': str(precondition._id)
            }
        )

    def _create_precondition(self, title, user, category_id, condition=None):
        p = model.Precondition(
                _owner=user._id,
                _category=category_id,
                title=title,
                type='simple',
                condition=condition or {}
        )
        DBSession.flush(p)
        return p

    def _get_qa(self, title):
        return model.Qa.query.get(title=title)

