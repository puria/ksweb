# -*- coding: utf-8 -*-
import json

from ksweb.lib.importers.base_importer import BaseImporter


class JsonImporter(BaseImporter):
    def convert(self):
        return json.loads(self.file_content.decode('utf-8'))
