import itertools

# pylint: disable=abstract-method
from .base import PactBase

class PactCollection(PactBase):


    def __init__(self, pacts=None, timeout_seconds=None):
        if pacts is None:
            pacts = []
        self._pacts = list(pacts)
        self._finished_pacts = []
        super(PactCollection, self).__init__(timeout_seconds)

    def __iter__(self):
        return itertools.chain(self._pacts, self._finished_pacts)

    def __iadd__(self, other):
        self.add(other)
        return self

    def add(self, pact):
        self._pacts.append(pact)

    def __repr__(self):
        return repr(list(self._pacts))
