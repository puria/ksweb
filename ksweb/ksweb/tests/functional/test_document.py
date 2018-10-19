# -*- coding: utf-8 -*-
from ksweb.tests import TestController
from ksweb import model


class TestDocument(TestController):
    application_under_test = 'main'

    def setUp(self):
        TestController.setUp(self)
        self.category = self._get_category('Area 1')

    def test_access_permission_not_garanted(self):
        self.app.get('/document/', status=302)

    def test_access_permission_admin(self):
        self._login_admin()
        resp_admin = self.app.get('/document', params=dict(workspace=self.category._id))
        assert resp_admin.status_code == 200

    def test_access_permission_lawyer(self):
        self._login_lawyer()
        resp_lawyer = self.app.get('/document', params=dict(workspace=self.category._id))
        assert resp_lawyer.status_code == 200

    def test_new_document(self):
        self._login_admin()
        resp_admin = self.app.get('/document/new', params=dict(workspace=self.category._id))
        assert resp_admin.status_code == 200

    def test_creation_document(self):
        self._login_lawyer()
        category1 = self._get_category('Area 1')
        output1 = self._create_fake_output('Output1')
        document_params = {
            'title': 'Titolo documento 1',
            'workspace': str(category1._id),
            'html': 'Io sono il tuo editor #{%s}' % str(output1._id)
        }
        resp = self.app.post_json(
            '/document/post', params=document_params
        ).json

        document = model.Document.query.get(title=document_params['title'])

        assert document
        assert resp['errors'] is None, resp

    def test_document_edit(self):
        self.test_creation_document()
        doc1 = self._get_document_by_title('Titolo documento 1')

        resp = self.app.get('/document/edit', params={
            '_id': str(doc1._id),
            'workspace': doc1._category
        })
        assert str(doc1._id) in resp

    def test_document_put(self):
        self.test_creation_document()
        category1 = self._get_category('Area 1')
        original_document = self._get_document_by_title('Titolo documento 1')

        document_params = {
            '_id': str(original_document._id),
            'title': 'Aggiornato',
            'workspace': str(category1._id),
            'html': '<p>Io sono il tuo editor</p>',
            'content': []
        }
        resp = self.app.put_json(
            '/document/put', params=document_params
        ).json

        updated_document = self._get_document_by_title(document_params['title'])

        assert updated_document
        assert updated_document._id == original_document._id
        assert resp['errors'] is None, resp

    def test_human_readable_details(self):
        self._login_lawyer()
        document = self._create_fake_document("Document")
        resp = self.app.get('/document/human_readable_details', params={'_id': document._id})
        assert str(document._id) in resp

    def test_document_export(self):
        self._login_lawyer()
        document = self._create_fake_document("Document")
        response = self.app.get('/document/export', params=dict(_id=str(document._id)))
        assert b"Document" in response.body, response.body

    def test_document_import(self):
        self._login_lawyer()
        workspace = self._get_category("Area 1")
        response = self.app.post('/document/import_document',
                                 params=dict(workspace=str(workspace._id)),
                                 upload_files=[('file_import',
                                                'ksweb/tests/functional/document_to_import.json')])
        r = response.follow()
        assert "Document successfully imported!" in r
