from ksweb.model import Output, Precondition, Qa
from ksweb.tests.models import ModelTest
from nose.tools import eq_


class TestOutput(ModelTest):
    klass = Output
    attrs = dict(
        title='This is a super output',
    )

    def do_get_dependencies(self):
        qa = Qa(question=u'Bounshch',
                title='Super QA',
                type=Qa.TYPES.TEXT,
                answers=[])
        _filter = Precondition(
            title=u'marengous',
            condition=[qa._id, ""],
            type=Precondition.TYPES.SIMPLE,
        )
        return {
            'precondition': _filter,
            'html': "Hi @{%s}" % qa.hash,
        }

