from .collection import PactCollection


class PactChain(PactCollection):


    def _is_finished(self):
        if not self._pacts:
            return True
        if self._pacts[0].poll():
            self._finished_pacts.append(self._pacts.pop(0))
            return not self._pacts
        return False
