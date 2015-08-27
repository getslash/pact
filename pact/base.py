import functools
import logging
import sys

import waiting

from ._compat import reraise

_logger = logging.getLogger(__name__)


class PactBase(object):

    def __init__(self):
        super(PactBase, self).__init__()
        self._finished = False
        self._then = []
        self._during = []
        _logger.debug("%r was created", self)

    def _validate_can_add_callback(self):
        if self._finished:
            raise RuntimeError('Cannot append then callbacks after pact was finished')

    def finished(self):
        """Returns whether or not this pact is finished
        """
        if not self._finished:
            for d in self._during:
                d()

        was_finished = self._finished
        returned = self._finished = self._is_finished()
        exc_info = None

        if not was_finished and self._finished:
            for t in self._then:
                try:
                    t()
                except Exception:
                    if exc_info is None:
                        exc_info = sys.exc_info()
                    _logger.warn("Exception thrown from 'then' callback", exc_info=True)
        if exc_info is not None:
            reraise(*exc_info)

        return returned

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
        _logger.debug("Waiting for %r", self)
        try:
            waiting.wait(self.finished, waiting_for=self, **kwargs)
            _logger.debug("Finish waiting for %r", self)
        except Exception:
            _logger.debug("Exception was raised while waiting for %r", self, exc_info=True)
            raise

    def __repr__(self):
        raise NotImplementedError() # pragma: no cover
