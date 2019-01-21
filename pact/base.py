import flux
import functools
import logbook
import sys
import waiting
from ._compat import reraise
from waiting.exceptions import TimeoutExpired

_logger = logbook.Logger(__name__)


class PactBase(object):

    def __init__(self, timeout_seconds):
        super(PactBase, self).__init__()
        self._triggered = False # Make sure we only trigger 'then' once, even if using greenlets
        self._finished = False
        self._then = []
        self._lastly = []
        self._during = []
        self._timeout_callbacks = []
        self._end_time = None if timeout_seconds is None else flux.current_timeline.time() + timeout_seconds
        _logger.debug("{0!r} was created", self)

    def _validate_can_add_callback(self):
        if self._finished:
            raise RuntimeError('Cannot append then callbacks after pact was finished')

    def get_timeout_exception(self, exc_info): # pylint: disable=no-self-use, unused-argument
        """Returns exception to be used when wait() times out. Default reraises waiting.TimeoutExpired.
        """
        return None

    def is_finished(self):
        """Returns whether or not this pact is finished
        """
        return self._finished

    def poll(self):
        """Checks all predicates to see if we're finished
        """
        if self._finished:
            return True

        exc_info = self._process_callbacks('during')

        self._finished = self._is_finished()

        if self._finished and not self._triggered:
            self._triggered = True
            then_exc_info = self._process_callbacks('then')
            lastly_exc_info = self._process_callbacks('lastly')
            exc_info = exc_info or then_exc_info or lastly_exc_info

        if exc_info is not None:
            reraise(*exc_info)

        return self.is_finished()

    def _process_callbacks(self, name):
        exc_info = None
        for callback in getattr(self, '_{}'.format(name)):
            try:
                callback()
            except Exception: # pylint: disable=broad-except
                if exc_info is None:
                    exc_info = sys.exc_info()
                _logger.debug("Exception thrown from '{}' callback {!r} of {!r}", name, callback, self, exc_info=True)
        return exc_info

    def then(self, callback, *args, **kwargs):
        """Calls ``callback`` when this pact is finished
        """
        assert callable(callback)
        self._validate_can_add_callback()
        self._then.append(functools.partial(callback, *args, **kwargs))
        return self

    def lastly(self, callback, *args, **kwargs):
        """Calls ``callback`` when this pact is finished, after all 'then' callbacks
        """
        assert callable(callback)
        self._validate_can_add_callback()
        self._lastly.append(functools.partial(callback, *args, **kwargs))
        return self

    def during(self, callback, *args, **kwargs):
        """Calls ``callback`` periodically while waiting for the pact to finish
        """
        assert callable(callback)
        self._validate_can_add_callback()
        self._during.append(functools.partial(callback, *args, **kwargs))
        return self

    def on_timeout(self, callback, *args, **kwargs):
        """Calls ``callback`` when a wait timeout is encountered
        """
        assert callable(callback)
        self._validate_can_add_callback()
        self._timeout_callbacks.append(functools.partial(callback, *args, **kwargs))
        return self

    def _is_finished(self):
        raise NotImplementedError()  # pragma: no cover

    def wait(self, **kwargs):
        """Waits for this pact to finish
        """
        _logger.debug("Waiting for {!r}...", self)
        start_time = flux.current_timeline.time()
        if 'timeout_seconds' not in kwargs and self._end_time is not None:
            kwargs['timeout_seconds'] = max(0, self._end_time - start_time)
        try:
            waiting.wait(self.poll, waiting_for=self, **kwargs)
        except TimeoutExpired:
            exc_info = sys.exc_info()
            for timeout_callback in self._timeout_callbacks:
                timeout_callback()
            exc = self.get_timeout_exception(exc_info)  # pylint: disable=assignment-from-none
            if exc is None:
                reraise(*exc_info)
            else:
                raise exc # pylint: disable=raising-bad-type
        except Exception:
            _logger.debug("Exception was raised while waiting for {!r}", self, exc_info=True)
            raise
        else:
            finish_time = flux.current_timeline.time()
            _logger.debug("Finished waiting for {!r} (took: {:.04f} sec)", self, finish_time - start_time)

    def __repr__(self):
        raise NotImplementedError() # pragma: no cover
