from datetime import datetime

from bson import ObjectId
from ming import schema as s
from ming.odm import FieldProperty, ForeignIdProperty, RelationProperty, FieldPropertyWithMissingNone

from ming.odm.declarative import MappedClass
from tg.util import Bunch


class MappedEntity(MappedClass):
    STATUS = Bunch(
        READ="READ",
        UNREAD="UNREAD"
    )

    _id = FieldProperty(s.ObjectId)

    _owner = ForeignIdProperty('User')
    owner = RelationProperty('User')

    _category = ForeignIdProperty('Category')
    category = RelationProperty('Category')

    title = FieldProperty(s.String, required=True)
    public = FieldProperty(s.Bool, if_missing=True)
    visible = FieldProperty(s.Bool, if_missing=True)
    status = FieldProperty(s.OneOf(*STATUS.values()), required=True, if_missing=STATUS.UNREAD)
    created_at = FieldProperty(s.DateTime, if_missing=datetime.utcnow())
    auto_generated = FieldProperty(s.Bool, if_missing=False)

    @classmethod
    def unread_count(cls, workspace_id):
        return cls.query.find({'status': cls.STATUS.UNREAD, '_category': ObjectId(workspace_id)}).count() or ''

    @classmethod
    def mark_as_read(cls, workspace_id):
        cls.query.update({'status': cls.STATUS.UNREAD, '_category': ObjectId(workspace_id)}, {'$set': {'status': cls.STATUS.READ}})

    def __json__(self):
        from ksweb.lib.utils import to_dict
        _dict = to_dict(self)
        _dict['entity'] = self.entity
        return _dict