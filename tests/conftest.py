import flux
from forge import Forge

import pytest
from pact import Pact


@pytest.fixture
def callback(forge):
    return forge.create_wildcard_function_stub()


class Pred(object):

    _satisfied = False

    def satisfy(self):
        self._satisfied = True

    def __call__(self):
        return self._satisfied


class Checkpoint(object):

    called_times = 0

    def __call__(self):
        self.called_times += 1

    @property
    def called(self):
        return self.called_times > 0


@pytest.fixture
def checkpoint():
    return Checkpoint()


@pytest.fixture
def checkpoint1():
    return Checkpoint()


@pytest.fixture
def checkpoint2():
    return Checkpoint()

@pytest.fixture
def timed_predicate_factory(deadline):
    def factory():
        return lambda: flux.current_timeline.time() >= deadline
    return factory

@pytest.fixture
def timed_predicate(timed_predicate_factory):
    return timed_predicate_factory()

@pytest.fixture
def deadline(num_seconds):
    return flux.current_timeline.time() + num_seconds

@pytest.fixture
def num_seconds():
    return 10


@pytest.fixture
def pred1():
    return Pred()


@pytest.fixture
def pred2():
    return Pred()


@pytest.fixture
def forge(request):

    returned = Forge()

    @request.addfinalizer
    def cleanup():
        returned.verify()
        returned.restore_all_replacements()

    return returned


@pytest.fixture(autouse=True, scope='session')
def freeze_flux():
    flux.current_timeline.set_time_factor(0)


@pytest.fixture
def state():
    return State()


@pytest.fixture
def pact(state):
    return Pact('test pact').until(state.is_finished)


class State(object):

    def __init__(self):
        super(State, self).__init__()
        self._finished = False
        self.is_finished_call_count = 0

    def is_finished(self):
        self.is_finished_call_count += 1
        return self._finished

    def finish(self):
        self._finished = True
