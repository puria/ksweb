# -*- coding: utf-8 -*-
from ksweb.model import Workspace, DBSession
from ksweb.tests import TestController


class TestWorkspace(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)

    def test_access_permission_not_garanted(self):
        self.app.get('/workspace/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/workspace')
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/workspace')
        assert resp_lawyer.status_code == 200

    def test_get_one(self):
        self._login_lawyer()
        workspace1 = self._get_workspace('Area 1')
        resp = self.app.get('/workspace/get_one', params={'id': str(workspace1._id)})
        assert str(workspace1._id) in resp

    def test_get_all(self):
        self._login_lawyer()
        workspace1 = self._get_workspace('Area 1')
        workspace2 = self._get_workspace('Area 2')

        resp = self.app.get('/workspace/get_all')
        assert str(workspace1._id) in resp
        assert str(workspace2._id) in resp

    def test_invisble_workspaces(self):
        iw = Workspace(name="invisible", visible=False)
        DBSession.flush(iw)

        self._login_lawyer()
        resp = self.app.get('/workspace/get_all')
        w = self._get_workspace('invisible')
        assert str(w._id) not in resp

    def test_create_workspace(self):
        self._login_lawyer()
        self.app.post_json(
            '/workspace/create',
            params=dict(
                workspace_name='Workspace',
            )
        )
        workspace = self._get_workspace('Workspace')
        assert workspace

    def test_check_duplicate_workspace(self):
        self.test_create_workspace()
        self.app.post_json(
            '/workspace/create',
            params=dict(
                workspace_name='Workspace',
            ),
            status=412
        )

    def test_workspace_delete(self):
        self.test_create_workspace()
        workspace = self._get_workspace("Workspace")
        self.app.post_json(
            '/workspace/delete',
            params={'workspace_id': str(workspace._id)}
        )
        c = self._get_workspace("Workspace")
        response = self.app.get('/workspace/get_all')
        assert not c
        assert str(workspace._id) not in response


    def test_workspace_without_owner_delete(self):
        self._login_lawyer()
        self.app.post_json('/workspace/create', params=dict(workspace_name='Workspace',))
        workspace = self._get_workspace('Workspace')
        workspace._owner = None
        workspace.owner = None
        self.app.post_json('/workspace/delete', params={'workspace_id': str(workspace._id)})
        c = self._get_workspace("Workspace")
        assert c
