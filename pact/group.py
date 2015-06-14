from .base import PactBase
from .utils import GroupWaitPredicate


class PactGroup(PactBase):

    def __init__(self, pacts=None):
        self._pacts = [] if pacts is None else list(pacts)
        super(PactGroup, self).__init__()

    def __iadd__(self, other):
        self.add(other)
        return self

    def add(self, pact, absorb=False):
        if absorb and isinstance(pact, PactGroup):
            if isinstance(pact, PactGroup):
                raise NotImplementedError('Absorbing groups is not supported') # pragma: no cover
        self._pacts.append(pact)
        if absorb:
            while pact._then:
                # then might throw, so we attempt it first
                self.then(pact._then[0])
                pact._then.pop(0)

    def _is_finished(self):
        return all(p.finished() for p in self._pacts)

    def _build_wait_predicate(self):
        return GroupWaitPredicate(self._pacts)

    def __str__(self):
        return ", ".join(map(str, self._pacts))
