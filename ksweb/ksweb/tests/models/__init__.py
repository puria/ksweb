# -*- coding: utf-8 -*-
"""Unit test suite for the models of the application."""

from nose.tools import eq_
from tg import config
from ksweb.tests import load_app
from ksweb.tests import setup_db, teardown_db

__all__ = ['ModelTest']


def setup():
    """Setup test fixture for all model tests."""
    load_app()
    setup_db()


def teardown():
    """Tear down test fixture for all model tests."""
    teardown_db()


class ModelTest(object):
    """Base unit test case for the models."""

    klass = None
    attrs = {}

    def setUp(self):
        """Setup test fixture for each model test method."""
        try:
            new_attrs = {}
            new_attrs.update(self.attrs)
            new_attrs.update(self.do_get_dependencies())
            self.obj = self.klass(**new_attrs)
            self.obj.__mongometa__.session.flush()
            self.obj.__mongometa__.session.clear()
            return self.obj
        except:
            datastore = config['pylons.app_globals'].ming_datastore
            try:
                # On MIM drop all data
                datastore.conn.clear_all()
            except:
                # On MongoDB drop database
                datastore.conn.drop_database(datastore.db)
            raise

    def tearDown(self):
        """Tear down test fixture for each model test method."""
        datastore = config['pylons.app_globals'].ming_datastore
        try:
            # On MIM drop all data
            datastore.conn.clear_all()
        except:
            # On MongoDB drop database
            datastore.conn.drop_database(datastore.db)

    def do_get_dependencies(self):
        """Get model test dependencies.

        Use this method to pull in other objects that need to be created
        for this object to be build properly.

        """
        return {}

    def test_create_obj(self):
        """Model objects can be created"""
        pass

    def test_query_obj(self):
        """Model objects can be queried"""
        obj = self.klass.query.find({}).first()
        for key, value in self.attrs.items():
            eq_(getattr(obj, key), value)
