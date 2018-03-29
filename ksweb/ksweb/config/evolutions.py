from ming.odm import mapper
from tgext.evolve import Evolution

from ksweb.model import Category, DBSession


class WorkspaceEvolution(Evolution):
    evolution_id = 'workspaces_evolution'

    def evolve(self):
        collection = mapper(Category).collection
        DBSession.drop_indexes(collection)
        DBSession.ensure_indexes(collection)
        DBSession.flush_all()


evolutions = [
    WorkspaceEvolution,
]
