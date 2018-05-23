# -*- coding: utf-8 -*-
"""
Integration tests for the :mod:`repoze.who`-powered authentication sub-system.

As ksweb grows and the authentication method changes, only these tests
should be updated.

"""
from __future__ import unicode_literals

from nose.tools import eq_, ok_

from ksweb.tests import TestController


class TestAuthentication(TestController):
    """
    Tests for the default authentication setup.

    If your application changes how the authentication layer is configured
    those tests should be updated accordingly
    """

    application_under_test = 'main'
    def test_forced_login(self):
        """Anonymous users are forced to login

        Test that anonymous users are automatically redirected to the login
        form when authorization is denied. Next, upon successful login they
        should be redirected to the initially requested page.

        """
        # Requesting a protected area
        resp = self.app.get('/admin/', status=302)
        ok_(resp.location.startswith('http://localhost/login'))
        # Getting the login form:
        resp = resp.follow(status=200)
        form = resp.form
        # Submitting the login form:
        form['login'] = 'admin'
        form['password'] = 'adminks'
        post_login = form.submit(status=302)
        # Being redirected to the initially requested page:
        ok_(post_login.location.startswith('http://localhost/post_login'))
        initial_page = post_login.follow(status=302)
        ok_('authtkt' in initial_page.request.cookies,
            "Session cookie wasn't defined: %s" % initial_page.request.cookies)
        ok_(initial_page.location.startswith('http://localhost/admin/'),
            initial_page.location)

    def test_voluntary_login(self):
        """Voluntary logins must work correctly"""
        # Going to the login form voluntarily:
        resp = self.app.get('/login', status=200)
        form = resp.form
        # Submitting the login form:
        form['login'] = 'admin'
        form['password'] = 'adminks'
        post_login = form.submit(status=302)
        # Being redirected to the home page:
        ok_(post_login.location.startswith('http://localhost/post_login'))
        home_page = post_login.follow(status=302)
        ok_('authtkt' in home_page.request.cookies,
            'Session cookie was not defined: %s' % home_page.request.cookies)
        eq_(home_page.location, 'http://localhost/')

    def test_logout(self):
        """Logouts must work correctly"""
        # Logging in voluntarily the quick way:
        resp = self.app.get('/login_handler?login=admin&password=adminks',
                            status=302)
        resp = resp.follow(status=302)
        ok_('authtkt' in resp.request.cookies,
            'Session cookie was not defined: %s' % resp.request.cookies)
        # Logging out:
        resp = self.app.get('/logout_handler', status=302)
        ok_(resp.location.startswith('http://localhost/post_logout'))
        # Finally, redirected to the home page:
        home_page = resp.follow(status=302)
        authtkt = home_page.request.cookies.get('authtkt')
        ok_(not authtkt or authtkt == 'INVALID',
            'Session cookie was not deleted: %s' % home_page.request.cookies)
        eq_(home_page.location, 'http://localhost/')

    def test_failed_login_keeps_username(self):
        """Wrong password keeps user_name in login form"""
        resp = self.app.get('/login_handler?login=admin&password=badpassword',
                            status=302)
        resp = resp.follow(status=200)
        ok_('Invalid Password' in resp, resp)
        eq_(resp.form['login'].value, 'admin')

    def test_user_not_found(self):
        resp = self.app.get('/login_handler?login=badadmin&password=badpassword',
                            status=302)
        resp = resp.follow(status=200)
        ok_('User not found' in resp, resp)
        eq_(resp.form['login'].value, 'badadmin')

