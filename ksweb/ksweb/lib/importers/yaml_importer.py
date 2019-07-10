import yaml
from ksweb.lib.importers.base_importer import BaseImporter


class YamlImporter(BaseImporter):
    def convert(self):
        return yaml.full_load(self.file_content.decode("utf-8"))
