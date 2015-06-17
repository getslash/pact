from .utils import EdgeTriggered
from .base import PactBase
from .group import PactGroup


class Pact(PactBase):

    def __init__(self, msg):
        self.msg = msg
        super(Pact, self).__init__()
        self._until = []

    def until(self, predicate, *args, **kwargs):
        """Adds a callback criterion for the completion of this pact

        :param predicate: A callable that should return a True-ish value once the end condition is met

        .. note:: When adding multiple predicates via multiple calls to until(), the pact waits on *all* of them to be
          satisfied
        """
        self._validate_can_add_callback()
        self._until.append(EdgeTriggered(predicate, args, kwargs))
        return self

    def _is_finished(self):
        return all(u.satisfied() for u in self._until)

    def group_with(self, other):
        return PactGroup([self, other])

    def _build_wait_predicate(self):
        return GroupWaitPredicate([self])

    def __repr__(self):
        return '<Pact: {0}>'.format(self.msg)
