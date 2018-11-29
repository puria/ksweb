# -*- coding: utf-8 -*-
"""The application's model objects"""

import ming.odm
from .session import mainsession, DBSession


def init_model(engine):
    """Call me before using any of the tables or classes in the model."""
    mainsession.bind = engine
    ming.odm.Mapper.compile_all()

    for mapper in ming.odm.Mapper.all_mappers():
        mainsession.ensure_indexes(mapper.collection)


# Import your model modules here.
from ksweb.model.auth import User, Group, Permission
from ksweb.model.qa import Qa
from ksweb.model.precondition import Precondition
from ksweb.model.output import Output
from ksweb.model.document import Document
from ksweb.model.questionary import Questionary
from ksweb.model.workspace import Workspace

__all__ = ['User', 'Group', 'Permission', 'Workspace', 'Qa', 'Precondition', 'Output', 'Document', 'Questionary']
