# -*- coding: utf-8 -*-
from functools import partial
from itertools import chain
from operator import is_not

from bson import ObjectId
from ksweb.lib.utils import find_entities_from_html
from ksweb.model import Precondition, Qa, Output, DBSession, Document
from ksweb.model.mapped_entity import MappedEntity


class BaseImporter(object):
    def __init__(self, file_content, workspace, owner):
        self.owner = owner
        self.imported = set()
        self.converted = dict()
        self.workspace = workspace
        self.file_content = file_content
        self.to_be_imported = self.convert()
        self.__new_properties = {
            '_owner': self.owner,
            'auto_generated': True,
            '_category': self.workspace,
            'status': MappedEntity.STATUS.UNREAD,
        }

    def __import_outputs(self):
        for o in self.to_be_imported['outputs']:
            self.__import_output(o)

    def __import_output(self, oid):
        duplicate = self.__get_already_imported(oid)
        if duplicate:
            return duplicate
        o = self.to_be_imported['outputs'].get(oid, None)
        if o.get('_precondition', None):
            __ = self.__import_filter(o['_precondition'])
            o['_precondition'] = str(__._id)
        os, qas = find_entities_from_html(o.get('html'))
        for nested_output in os:
            new_output = self.__import_output(nested_output)
            o['html'] = o['html'].replace(nested_output, str(new_output._id))
        for qa in qas:
            new_qa = self.__import_qa(qa)
            o['html'] = o['html'].replace(qa, str(new_qa._id))
        return self.__upsert_document(Output, oid, o)

    def __import_filter(self, fid):
        if fid in self.to_be_imported['simple_preconditions']:
            return self.__import_simple_filter(fid)
        if fid in self.to_be_imported['advanced_preconditions']:
            return self.__import_advanced_filter(fid)
        return self.__get_already_imported(fid)

    def __import_simple_filter(self, fid):
        f = self.to_be_imported['simple_preconditions'][fid]
        qa = f['condition'][0]
        new = self.__import_qa(qa)
        f['condition'][0] = str(new._id)
        return self.__upsert_document(Precondition, fid, f)

    def __import_advanced_filter(self, fid):
        f = self.to_be_imported['advanced_preconditions'][fid]
        f['condition'] = [str(self.__import_filter(__)._id) if __ not in Precondition.PRECONDITION_OPERATOR else __ for __ in f['condition']]
        return self.__upsert_document(Precondition, fid, f)

    def __import_qa(self, qid):
        duplicate = self.__get_already_imported(qid)
        if duplicate:
            return duplicate
        qa = self.to_be_imported['qa'].get(qid, None)
        if qa.get('_parent_precondition', None):
            __ = self.__import_filter(qa['_parent_precondition'])
            qa['_parent_precondition'] = str(__._id)
        return self.__upsert_document(Qa, qid, qa)

    def __get_already_imported(self, _id):
        if _id in self.converted:
            return next((__ for __ in self.imported if str(__._id) == self.converted[_id]), None)
        return next((__ for __ in self.imported if str(__._id) == _id), None)

    def __find_stored_entity(self, cls, _id, body):
        body['_owner'] = self.owner
        body['_category'] = self.workspace
        if '_precondition' in body.keys():
            body['_precondition'] = ObjectId(body['_precondition']) if body['_precondition'] else None
        find_by_body = cls.query.find(body).first()
        find_by_id = cls.query.get(_id=ObjectId(_id))
        found = list(filter(partial(is_not, None), [find_by_body, find_by_id]))
        if found:
            return self.__add_to_conversion_table(_id, found[0])
        return None

    def __add_to_conversion_table(self, old_id, new_entity):
        if old_id == str(new_entity._id):
            return
        self.converted[old_id] = str(new_entity._id)
        self.imported.add(new_entity)
        return new_entity

    def __upsert_document(self, cls, _id, body):
        filter_out = ['_id', 'entity', 'auto_generated', 'status']
        body = {k: v for k, v in body.items() if k not in filter_out}
        found = self.__find_stored_entity(cls, _id, body)
        if found:
            return found
        body.update(self.__new_properties)
        inserted = cls(**body)
        return self.__add_to_conversion_table(_id, inserted)

    def create_document(self):
        html = self.to_be_imported['html']
        for old, new in self.converted.items():
            html = html.replace(old, new)
        return Document(
            html=html,
            _owner=self.owner,
            _category=self.workspace,
            tags=self.to_be_imported['tags'],
            title=self.to_be_imported['title'],
            public=self.to_be_imported['public'],
            status=self.to_be_imported['status'],
            license=self.to_be_imported['license'],
            version=self.to_be_imported['version'],
            visible=self.to_be_imported['visible'],
            description=self.to_be_imported['description'],
        )

    def convert(self):
        return self.file_content

    def run(self):
        self.__import_outputs()
        self.create_document()
