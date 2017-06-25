import pact
import flux
import pytest
from waiting.exceptions import TimeoutExpired


@pytest.mark.parametrize('reprify', [repr, str])
def test_str_repr(reprify):
    msg = 'Some message here'
    p = pact.Pact(msg)
    assert msg in reprify(p)


def test_pact_is_finished_doesnt_poll(pact, state):
    assert not pact.is_finished()
    assert state.is_finished_call_count == 0


def test_pact_is_finished_not_called_after_finish_poll(pact, state):
    assert state.is_finished_call_count == 0
    assert not pact.poll()
    assert not pact.poll()
    assert state.is_finished_call_count == 2
    state.finish()
    assert pact.poll()
    assert pact.poll()
    assert state.is_finished_call_count == 3


def test_add_pact_callback_after_pact_finished(pact, state, pact_callback, forge, callback):
    assert not pact.is_finished()
    # expect
    callback(1).and_return(True)

    forge.replay()

    pact_callback(callback, 1)

    state.finish()
    assert pact.poll() and pact.is_finished()
    with pytest.raises(RuntimeError):
        pact_callback(callback)

    forge.verify()


def test_add_not_callable_to_pact_fails(pact, pact_callback):
    with pytest.raises(AssertionError):
        pact_callback(True)


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
        pact.poll()

    forge.verify()
    assert pact.is_finished()


def test_on_timeout(pact, callback, forge):
    callback(1)
    callback(2)
    pact.on_timeout(callback, 1).on_timeout(callback, 2)

    forge.replay()
    with pytest.raises(TimeoutExpired):
        pact.wait(timeout_seconds=3)


def test_wait_no_timeout_seconds_throws_after_duration(pact_duration, num_seconds):
    time_before = flux.current_timeline.time()
    with pytest.raises(TimeoutExpired):
        pact_duration.wait()
    assert num_seconds == flux.current_timeline.time() - time_before


def test_wait_no_timeout_seconds_called_after_duration_passed_immediately_throws(pact_duration, num_seconds):
    time_first = flux.current_timeline.time()
    flux.current_timeline.set_time(time_first + num_seconds + 1)
    time_before = flux.current_timeline.time()
    with pytest.raises(TimeoutExpired):
        pact_duration.wait()
    assert time_before == flux.current_timeline.time()


def test_wait_with_timeout_seconds_and_duration_throws_after_timeout_seconds(pact_duration, num_seconds):
    timeout = num_seconds + 1
    time_before = flux.current_timeline.time()
    with pytest.raises(TimeoutExpired):
        pact_duration.wait(timeout_seconds=timeout)
    assert timeout == flux.current_timeline.time() - time_before


def test_wait_with_timeout_seconds_and_duration_throws_after_timeout_seconds_duration_smaller(pact_duration, num_seconds):
    timeout = num_seconds - 1
    time_before = flux.current_timeline.time()
    with pytest.raises(TimeoutExpired):
        pact_duration.wait(timeout_seconds=timeout)
    assert timeout == flux.current_timeline.time() - time_before


def test_duration_doesnt_effect_finished_pacts(pact_duration, state):
    state.finish()
    time_before = flux.current_timeline.time()
    pact_duration.wait()
    assert time_before == flux.current_timeline.time()
    assert pact_duration.poll() and pact_duration.is_finished()


class SampleException(Exception):
    pass


@pytest.fixture(params=['then', 'until', 'during'])
def pact_callback(request, pact):
    name = request.param
    return getattr(pact, name)
