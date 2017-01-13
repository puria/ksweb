# -*- coding: utf-8 -*-
from ksweb.tests import TestController


class TestOutput(TestController):

    def test_get_one(self):
        category1 = self._get_category('Categoria 1')
        resp = self.app.get('/category/get_one', params={'id': str(category1._id)})
        assert category1._id in resp

    def test_get_all(self):
        category1 = self._get_category('Categoria 1')
        category2 = self._get_category('Categoria 2')
        category3 = self._get_category('Not Visible Category')

        resp = self.app.get('/category/get_all', params={'id': str(category1._id)})
        assert category1._id in resp
        assert category2._id in resp
        assert category3._id not in resp
