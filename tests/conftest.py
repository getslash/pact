import flux
from forge import Forge

import pytest
from pact import Pact


@pytest.fixture
def callback(forge):
    return forge.create_wildcard_function_stub()


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
