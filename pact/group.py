import itertools

from .base import PactBase


class PactGroup(PactBase):

    def __init__(self, pacts=None, lazy=True, timeout_seconds=None, poll_window=None):
        if poll_window is not None and lazy:
            raise ValueError("'lazy' and 'poll_window' are mutually exclusive")

        if pacts is None:
            pacts = []
        self._pacts = list(pacts)
        self._finished_pacts = []
        self._poll_window = 1 if lazy else poll_window
        super(PactGroup, self).__init__(timeout_seconds)

    def __iadd__(self, other):
        self.add(other)
        return self

    def __iter__(self):
        return itertools.chain(self._pacts, self._finished_pacts)

    def get_timeout_exception(self, exc_info):
        if self._pacts:
            return self._pacts[0].get_timeout_exception(exc_info)
        return super(PactGroup, self).get_timeout_exception(exc_info)

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
            while pact._lastly:
                # lastly might throw, so we attempt it first
                self.lastly(pact._lastly[0])
                pact._lastly.pop(0)

    def _is_finished(self):
        indexes_to_remove = []

        unfinished = 0
        for index, pact in enumerate(self._pacts):
            if pact.poll():
                indexes_to_remove.append(index)
            else:
                if self._poll_window:
                    unfinished += 1
                    if unfinished == self._poll_window:
                        break

        for index in reversed(indexes_to_remove):
            self._finished_pacts.append(self._pacts.pop(index))

        return not bool(self._pacts)

    def __repr__(self):
        return repr(list(self._pacts))
