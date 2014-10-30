import waiting

from .utils import EdgeTriggered, GroupWaitPredicate
from .base import PactBase
from .group import PactGroup


class Pact(PactBase):

    def __init__(self, msg):
        super(Pact, self).__init__()
        self.msg = msg
        self._until = []

    def until(self, callback, *args, **kwargs):
        """Adds a callback criterion for the completion of this pact
        """
        self._until.append(EdgeTriggered(callback, args, kwargs))
        return self

    def _is_finished(self):
        return all(u.satisfied() for u in self._until)

    def group_with(self, other):
        return PactGroup([self, other])

    def _build_wait_predicate(self):
        return GroupWaitPredicate([self])

    def __repr__(self):
        return self.msg
