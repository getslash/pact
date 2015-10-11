import functools
import logbook
import sys

import waiting

from ._compat import reraise

_logger = logbook.Logger(__name__)


class PactBase(object):

    def __init__(self):
        super(PactBase, self).__init__()
        self._finished = False
        self._then = []
        self._during = []
        _logger.debug("{0!r} was created", self)

    def _validate_can_add_callback(self):
        if self._finished:
            raise RuntimeError('Cannot append then callbacks after pact was finished')

    def is_finished(self):
        """Returns whether or not this pact is finished
        """
        return self._finished

    def poll(self):
        """Checks all predicates to see if we're finished
        """
        if self._finished:
            return True

        for d in self._during:
            d()

        returned = self._finished = self._is_finished()
        exc_info = None

        if self._finished:
            for t in self._then:
                try:
                    t()
                except Exception:
                    if exc_info is None:
                        exc_info = sys.exc_info()
                    _logger.debug("Exception thrown from 'then' callback", exc_info=True)
        if exc_info is not None:
            reraise(*exc_info)

        return self.is_finished()


    def finished(self):
        """Deprecated. Use poll() or is_finished() instead
        """
        _logger.warning('Pact.finished() is deprecated. Use poll() and/or is_finished() instead')
        self.poll()
        return self.is_finished()


    def then(self, callback, *args, **kwargs):
        """Calls ``callback`` when this pact is finished
        """
        self._validate_can_add_callback()
        self._then.append(functools.partial(callback, *args, **kwargs))
        return self

    def during(self, callback, *args, **kwargs):
        """Calls ``callback`` periodically while waiting for the pact to finish
        """
        self._validate_can_add_callback()
        self._during.append(functools.partial(callback, *args, **kwargs))
        return self

    def _is_finished(self):
        raise NotImplementedError()  # pragma: no cover

    def group_with(self, other):
        raise NotImplementedError()  # pragma: no cover

    def __add__(self, other):
        return self.group_with(other)

    def wait(self, **kwargs):
        """Waits for this pact to finish
        """
        _logger.debug("Waiting for {0!r}", self)
        try:
            waiting.wait(self.poll, waiting_for=self, **kwargs)
            _logger.debug("Finish waiting for {0!r}", self)
        except Exception:
            _logger.debug("Exception was raised while waiting for {0!r}", self, exc_info=True)
            raise

    def __repr__(self):
        raise NotImplementedError() # pragma: no cover
