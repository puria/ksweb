# -*- coding: utf-8 -*-
"""
Functional test suite for the root controller.

This is an example of how functional tests can be written for controllers.

As opposed to a unit-test, which test a small unit of functionality,
functional tests exercise the whole application and its WSGI stack.

Please read http://pythonpaste.org/webtest/ for more information.

"""

from nose.tools import ok_

from ksweb.tests import TestController


class TestRootController(TestController):
    application_under_test = 'main'

    """Tests for the method in the root controller."""
    def test_index(self):
        self._login_lawyer()
        resp = self.app.get('/')

    def test_index_redirect(self):
        """The front page is working properly"""
        resp = self.app.get('/', status=200)

    def test_privacy(self):
        self.app.get('/privacy', status=200)

    def test_terms(self):
        self.app.get('/terms', status=200)