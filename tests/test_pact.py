import pact

import pytest


@pytest.mark.parametrize('reprify', [repr, str])
def test_str_repr(reprify):
    msg = 'Some message here'
    p = pact.Pact(msg)
    assert msg in reprify(p)


def test_pact_is_finished_not_called_after_finish(pact, state):
    assert state.is_finished_call_count == 0
    assert not pact.finished()
    assert not pact.finished()
    assert state.is_finished_call_count == 2
    state.finish()
    assert pact.finished()
    assert pact.finished()
    assert state.is_finished_call_count == 3


def test_add_pact_callback_after_pact_finished(pact, state, pact_callback, forge, callback):
    assert not pact.finished()
    # expect
    callback(1).and_return(True)

    forge.replay()

    pact_callback(callback, 1)

    state.finish()
    assert pact.finished()
    with pytest.raises(RuntimeError):
        pact_callback(callback)

    forge.verify()

def test_then_exception(pact, state, forge, callback):
    callback(1)
    callback(2).and_raise(SampleException())
    callback(3)

    forge.replay()

    pact.then(callback, 1)
    pact.then(callback, 2)
    pact.then(callback, 3)


    state.finish()
    with pytest.raises(SampleException):
        pact.finished()

    forge.verify()
    assert pact.finished()

class SampleException(Exception):
    pass

@pytest.fixture(params=['then', 'until', 'during'])
def pact_callback(request, pact):
    name = request.param
    return getattr(pact, name)
