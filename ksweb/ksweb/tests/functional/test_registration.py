# -*- coding: utf-8 -*-
from ksweb import model
from ksweb.tests import TestController
from tgext.pluggable import app_model


class TestRegistration(TestController):
    application_under_test = 'main'

    def test_registration(self):
        resp = self.app.get('/registration', status=200)
        form = resp.form
        form['user_name'] = "fake_ks_user"
        form['email_address'] = "registration.ksweb@kswebtest.it"
        form['password'] = "12345"
        form['password_confirm'] = "12345"
        resp = form.submit()
        resp = resp.follow(status=200)
        assert "Registration Completed" in resp, resp

    def test_after_activation(self):
        resp = self.app.get('/registration', status=200)
        form = resp.form
        form['user_name'] = "fake_ks_user"
        form['email_address'] = "registration.ksweb@kswebtest.it"
        form['password'] = "12345"
        form['password_confirm'] = "12345"
        resp = form.submit()
        resp = resp.follow(status=200)

        registration = app_model.Registration.query.find({'email_address':'registration.ksweb@kswebtest.it'}).first()

        resp = self.app.get('/registration/activate?code=%s' % registration.code, status=302)
        #  Check if user has been created
        user = model.User.query.find({'email_address': 'registration.ksweb@kswebtest.it'}).first()
        assert user is not None
