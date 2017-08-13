from .collection import PactCollection
from .chain import PactChain


class PactGroup(PactCollection):

    def __init__(self, pacts=None, lazy=True, timeout_seconds=None):
        self._is_lazy = lazy
        super(PactGroup, self).__init__(pacts, timeout_seconds)

    def add(self, pact, absorb=False): #pylint: disable=arguments-differ
        if absorb and isinstance(pact, PactGroup) or isinstance(pact, PactChain):
            raise NotImplementedError('Absorbing groups or chains is not supported') # pragma: no cover
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
        super(PactGroup, self).add(pact)

    def _is_finished(self):
        has_finished = True
        indices_to_remove = []
        for index, pact in enumerate(self._pacts):
            if pact.poll():
                indices_to_remove.append(index)
            else:
                has_finished = False
                if self._is_lazy:
                    break
        for index in reversed(indices_to_remove):
            self._finished_pacts.append(self._pacts.pop(index))
        return has_finished
