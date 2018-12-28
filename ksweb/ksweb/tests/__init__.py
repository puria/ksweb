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

try:
    unicode
except NameError:
    unicode = str

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
        w = model.Workspace(name="Area 1", visible=True)
        w2 = model.Workspace(name="Area 2", visible=True)
        DBSession.flush(w)
        DBSession.flush(w2)

    def tearDown(self):
        """Tear down test fixture for each functional test method."""
        teardown_db()

    def _login_admin(self):
        self.app.get(
            '/login_handler?login=admin&password=adminks', status=302
        )

    def _login_lawyer(self):
        self.app.get('/login_handler?login=lawyer&password=lawyerks', status=302)

    def _get_user(self, email_address):
        return model.User.query.get(email_address=email_address)

    #  Rewrite utility method for test
    #  Workspace Utility
    def _get_workspace(self, name):
        return model.Workspace.query.get(name=name)

    def _create_workspace(self, name, visible=True):
        c = model.Workspace(
                name=name,
                visible=visible,
        )
        DBSession.flush(c)
        return c

    def _get_or_create_workspace(self, name, visible=True):
        c = self._get_workspace(name)
        if c:
            return c
        return self._create_workspace(name, visible)

    #  Question And Answer Utility
    def _get_qa(self, id):
        return model.Qa.query.get(_id=ObjectId(id))

    def _get_qa_by_title(self, title):
        return model.Qa.query.get(title=title)

    def _create_qa(self, title, workspace_id, question, tooltip, link, qa_type, answers):
        self.app.post_json(
            '/qa/post', params={
                'title': title,
                'workspace': str(workspace_id),
                'question': question,
                'tooltip': tooltip,
                'link': link,
                'answer_type': qa_type,
                'answers': answers
            }
        )
        return self._get_qa_by_title(title)

    def _get_or_create_qa(self, title, workspace_id=None, question=None, tooltip=None, link=None, qa_type=None, answers=None):
        qa = self._get_qa_by_title(title)
        return qa if qa else self._create_qa(title, workspace_id, question, tooltip, link, qa_type, answers)

    def _create_fake_qa(self, title, qa_type='single', answers=FAKE_RESPONSE):
        fake_workspace = self._get_or_create_workspace('fake_workspace')
        return self._create_qa(
            title,
            fake_workspace._id,
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

    def _create_simple_precondition(self, title, workspace_id, qa_id, answer_type='what_response', interested_response=[]):
        """
        answer_type = ['have_response', what_response]
        """
        self.app.post_json(
            '/precondition/simple/post', params={
                'title': title,
                'workspace': str(workspace_id),
                'question': str(qa_id),
                'answer_type': answer_type,
                'interested_response': interested_response
            }
        )
        return self._get_precond_by_title(title)

    def _create_fake_simple_precondition(self, title, workspace_id=None):
        if not workspace_id:
            workspace_id = self._get_or_create_workspace("Fake_cat_%s" % title)._id

        qa = self._create_fake_qa(title)
        return self._create_simple_precondition(title, workspace_id, qa._id, 'what_response', [self.FAKE_RESPONSE[0]])

    def _create_advanced_precondition(self, title, workspace_id, conditions=[]):
        self.app.post_json(
            '/precondition/advanced/post', params={
                'title': title,
                'workspace': str(workspace_id),
                'conditions': conditions
            }
        )
        return self._get_precond_by_title(title)

    def _create_fake_advanced_precondition_red_animal(self, title):
        """
        Create a fake a advanced precondition with 3 element
        1 - Favourite color: Red
        2 - or
        3 - Animal liked: Pig or Dog
        :param title: title of the precondition
        :return: the created precondition
        """
        self._login_lawyer()
        workspace1 = self._get_workspace('Area 1')
        #  Devo creare almeno 1 qa con delle risposte

        qa_color_param = {
            'title': 'Favourite color',
            'workspace_id': str(workspace1._id),
            'question': 'What is your favourite color?',
            'tooltip': 'Favourite color',
            'link': 'http://www.axant.it',
            'qa_type': 'single',
            'answers': ['Red', 'Blu', 'Yellow', 'Green']
        }
        qa_color = self._create_qa(**qa_color_param)

        prec_red_color = {
            'title': 'Red is Favourite',
            'workspace': str(workspace1._id),
            'question': str(qa_color._id),
            'answer_type': 'what_response',
            'interested_response': ['Red']
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=prec_red_color
        )

        qa_animal_liked_param = {
            'title': 'Animal liked',
            'workspace_id': str(workspace1._id),
            'question': 'What animal do you like?',
            'tooltip': 'Animalsss',
            'link': 'http://www.axant.it',
            'qa_type': 'multi',
            'answers': ['Dog', 'Cat', 'Pig', 'Turtle', 'Rabbit']
        }
        qa_animal_liked = self._create_qa(**qa_animal_liked_param)

        prec_animal_liked_pig_dog = {
            'title': 'Like pig and dog',
            'workspace': str(workspace1._id),
            'question': str(qa_animal_liked._id),
            'answer_type': 'what_response',
            'interested_response': ['Pig', 'Dog']
        }
        resp = self.app.post_json(
            '/precondition/simple/post', params=prec_animal_liked_pig_dog
        )

        precond_red = self._get_precond_by_title(prec_red_color['title'])
        precond_pig_dog = model.Precondition.query.get(title=prec_animal_liked_pig_dog['title'])

        #  Ora che ho i 2  filtri posso creare quelli composti
        precond_advanced = {
            'title': title,
            'workspace': str(workspace1._id),
            'conditions': [
                {
                    'type': 'precondition',
                    'content': str(precond_red._id)
                },
                {
                    'type': 'operator',
                    'content': 'or'
                },
                {
                    'type': 'precondition',
                    'content': str(precond_pig_dog._id)
                 }
            ]
        }

        resp = self.app.post_json(
            '/precondition/advanced/post', params=precond_advanced
        )
        return self._get_precond_by_title(title)

    #  Output Utility
    def _get_output(self, id):
        return model.Output.query.get(_id=ObjectId(id))

    def _get_output_by_title(self, title):
        return model.Output.query.get(title=title)

    def _create_output(self, title, workspace_id=None, precondition_id=None, html=''):
        if not workspace_id:
            workspace_id = self._get_or_create_workspace("Fake_cat_%s" % title)._id
        resp = self.app.post_json(
            '/output/post', params={
                'title': title,
                'workspace': str(workspace_id),
                'precondition': str(precondition_id) if precondition_id else None,
                'html': html,
            }
        )
        print(resp)
        return self._get_output_by_title(title)

    def _create_fake_output(self, title, workspace_id=None):
        if not workspace_id:
            workspace_id = self._get_or_create_workspace("Fake_cat_%s" % title)._id
        return self._create_output(title, workspace_id,
                                   self._create_fake_simple_precondition(title)._id,
                                   "Fake html")

    def _get_document_by_title(self, title):
        return model.Document.query.get(title=title)

    def _create_document(self, title, workspace_id=None, html=None):
        if not workspace_id:
            workspace_id = self._get_or_create_workspace("Fake_cat_%s" % title)._id

        self.app.post_json(
            '/document/post', params={
                'title': title,
                'workspace': str(workspace_id),
                'html': html
            }
        ).json

        return self._get_document_by_title(title)

    def _create_fake_document(self, title, html=None, workspace_id=None):
        output1 = self._create_fake_output(title)
        html = html if html else "#{%s}" % str(output1.hash)
        return self._create_document(title, workspace_id, html)

    #  Questionary Utility
    def _get_questionary(self, id):
        return model.Questionary.query.get(_id=ObjectId(id))

    def _get_questionary_by_title(self, title):
        return model.Questionary.query.get(title=title)

    def _create_questionary(self, title, document_id):
        self.app.post_json('/questionary/create', params={
            'questionary_title': title,
            'document_id': str(document_id)
        })
        return self._get_questionary_by_title(title)

    def _create_fake_questionary(self, title, workspace_id=None):
        fake_doc = self._create_fake_document(title, workspace_id=None)
        self._create_questionary(title, fake_doc._id)

        return self._get_questionary_by_title(title)
