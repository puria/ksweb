# -*- coding: utf-8 -*-
from ksweb.tests import TestController


class TestCategory(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)

    def test_access_permission_not_garanted(self):
        self.app.get('/category/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/category')
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/category')
        assert resp_lawyer.status_code == 200

    def test_get_one(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        resp = self.app.get('/category/get_one', params={'id': str(category1._id)})
        assert category1._id in resp

    def test_get_all(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        category2 = self._get_category('Area 2')
        category3 = self._get_category('Not Visible Category')

        resp = self.app.get('/category/get_all')
        assert category1._id in resp
        assert category2._id in resp
        assert category3._id not in resp

    def test_create_category(self):
        self._login_lawyer()
        self.app.post_json(
            '/category/create',
            params=dict(
                workspace_name='Category',
            )
        )
        category = self._get_category('Category')
        assert category

    def test_check_duplicate_category(self):
        self.test_create_category()
        self.app.post_json(
            '/category/create',
            params=dict(
                workspace_name='Category',
            ),
            status=412
        )

    def test_category_delete(self):
        self.test_create_category()
        category = self._get_category("Category")
        self.app.post_json(
            '/category/delete',
            params={'workspace_id': str(category._id)}
        )
        c = self._get_category("Category")
        response = self.app.get('/category/get_all')
        assert not c
        assert category._id not in response


    def test_workspace_without_owner_delete(self):
        self._login_lawyer()
        self.app.post_json('/category/create', params=dict(workspace_name='Category',))
        category = self._get_category('Category')
        category._owner = None
        category.owner = None
        self.app.post_json('/category/delete', params={'workspace_id': str(category._id)})
        c = self._get_category("Category")
        assert c
