from .base import PactBase
from .utils import GroupWaitPredicate


class PactGroup(PactBase):

    def __init__(self, pacts):
        super(PactGroup, self).__init__()
        self._pacts = list(pacts)

    def _is_finished(self):
        return all(p.finished() for p in self._pacts)

    def _build_wait_predicate(self):
        return GroupWaitPredicate(self._pacts)

