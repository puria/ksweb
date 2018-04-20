# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.
Please read http://pythonpaste.org/webtest/ for more information.
"""
from ksweb import model

from ksweb.tests import TestController
from bson import ObjectId


class TestRootController(TestController):
    application_under_test = 'main'

    """Tests for the method in the root controller."""
    def test_index(self):
        self._login_lawyer()
        self.app.get('/')

    def test_index_redirect(self):
        """The front page is working properly"""
        self.app.get('/', status=200)

    def test_privacy(self):
        response = self.app.get('/privacy', status=200)
        assert 'PRIVACY POLICY' in response

    def test_terms(self):
        response = self.app.get('/terms', status=200)
        assert 'CONDIZIONI DI SERVIZIO' in response

    def test_start_without_login(self):
        self.app.get('/start', status=302)

    def test_start(self):
        self._login_lawyer()
        lawyer = self._get_user('lawyer1@ks.axantweb.com')
        response = self.app.get('/start', status=200)
        workspaces = model.Category.per_user(lawyer._id)
        workspaces_names = [__.name for __ in workspaces]

        assert all(name in response for name in workspaces_names)

    def test_dashboard_access(self):
        resp = self.app.get('/dashboard', params={'share_id': ObjectId()}).follow()
        resp = resp.follow()
        assert 'Login' in resp, resp.body

    def test_dashboard_no_forms(self):
        self._login_lawyer()
        lawyer = self._get_user('lawyer1@ks.axantweb.com')
        resp = self.app.get('/dashboard', params={'share_id': str(lawyer._id)}, status=302).follow()
        assert 'Select your workspace or create a new one' in resp, resp.body

    def test_start_sidebar_is_hidden(self):
        self._login_lawyer()
        response = self.app.get('/start', status=200)
        assert 'sidebar' not in response

    def test_legal(self):
        response = self.app.get('/legal', status=200)
        assert "ACCETTAZIONE ESPRESSA" in response

    def test_source(self):
        response = self.app.get('/source', status=200)
        assert 'puria' in response

    def test_login_not_found_user(self):
        response = self.app.get('/login', params=dict(failure='user-not-found'))
        assert 'User not found' in response

    def test_login_user_created(self):
        response = self.app.get('/login', params=dict(failure='user-created'))
        assert 'User successfully created' in response