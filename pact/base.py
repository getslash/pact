import waiting


class PactBase(object):

    def finished(self):
        raise NotImplementedError() # pragma: no cover

    def group_with(self, other):
        raise NotImplementedError() # pragma: no cover

    def __add__(self, other):
        return self.group_with(other)

    def wait(self, timeout_seconds=None):
        """Waits for this pact to finish
        """
        predicate = self._build_wait_predicate()
        waiting.wait(predicate, timeout_seconds=timeout_seconds, waiting_for=predicate)

    def _build_wait_predicate(self):
        raise NotImplementedError() # pragma: no cover
