import collections

from .base import PactBase


class PactGroup(PactBase):

    def __init__(self, pacts=None):
        if pacts is None:
            pacts = ()
        self._pacts = collections.deque(pacts)
        self._finished_pacts = []
        super(PactGroup, self).__init__()

    def __iadd__(self, other):
        self.add(other)
        return self

    def __iter__(self):
        return iter(self._pacts)

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
        finished_indices = []
        while self._pacts:
            p = self._pacts[0]
            if p.finished():
                self._finished_pacts.append(self._pacts.popleft())
            else:
                return False
        # no more pacts
        return True

    def __repr__(self):
        return repr(list(self._pacts))
