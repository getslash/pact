import itertools

from .base import PactBase


class PactGroup(PactBase):

    def __init__(self, pacts=None, lazy=True, timeout_seconds=None):
        if pacts is None:
            pacts = []
        self._pacts = list(pacts)
        self._finished_pacts = []
        self._is_lazy = lazy
        super(PactGroup, self).__init__(timeout_seconds)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __iter__(self):
        return itertools.chain(self._pacts, self._finished_pacts)

    def add(self, pact, absorb=False):
        if absorb and isinstance(pact, PactGroup):
            raise NotImplementedError('Absorbing groups is not supported') # pragma: no cover
        self._pacts.append(pact)
        if absorb:
            # pylint: disable=protected-access
            while pact._then:
                # then might throw, so we attempt it first
                self.then(pact._then[0])
                pact._then.pop(0)

    def _is_finished(self):
        has_finished = True
        indexes_to_remove = []
        for index, pact in enumerate(self._pacts):
            if pact.poll():
                indexes_to_remove.append(index)
            else:
                has_finished = False
                if self._is_lazy:
                    break
        for index in reversed(indexes_to_remove):
            self._finished_pacts.append(self._pacts.pop(index))
        return has_finished

    def __repr__(self):
        return repr(list(self._pacts))
