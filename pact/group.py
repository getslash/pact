from .base import PactBase
from .utils import GroupWaitPredicate


class PactGroup(PactBase):

    def __init__(self, pacts):
        super(PactGroup, self).__init__()
        self._pacts = list(pacts)

    def __iadd__(self, other):
        self._pacts.append(other)
        return self

    def _is_finished(self):
        return all(p.finished() for p in self._pacts)

    def _build_wait_predicate(self):
        return GroupWaitPredicate(self._pacts)

    def __str__(self):
        return ", ".join(map(str, self._pacts))
