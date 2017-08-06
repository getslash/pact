import pytest
import flux
from pact import Pact, PactGroup
from waiting.exceptions import TimeoutExpired

# pylint: disable=redefined-outer-name

def test_group_wait_during(checkpoint, timed_group, num_seconds):
    timed_group.during(checkpoint)
    timed_group.wait()
    assert checkpoint.called_times == num_seconds + 1


def test_group_wait_then(checkpoint, checkpoint1, checkpoint2, checkpoint3, timed_group, timed_pact):
    timed_group.lastly(checkpoint1)
    timed_group.then(checkpoint)
    timed_pact.then(checkpoint2)
    timed_pact.lastly(checkpoint3)
    timed_group.wait()
    assert checkpoint.called
    assert checkpoint1.called
    assert checkpoint2.called
    assert checkpoint3.called
    assert timed_group.is_finished()


@pytest.mark.parametrize('adding_group', [True, False])
def test_group_iadd_pact(adding_group):
    group = PactGroup()
    if adding_group:
        p1 = Pact('c') + Pact('d')
    else:
        p1 = Pact('c')
    group += p1
    assert group._pacts[-1] is p1  # pylint: disable=protected-access


def test_group_with_duration(pact, num_seconds):
    time_before = flux.current_timeline.time()
    group = PactGroup([pact], timeout_seconds=num_seconds)
    with pytest.raises(TimeoutExpired):
        group.wait()
    assert num_seconds == flux.current_timeline.time() - time_before


def test_group_with_duration_wait_timeout_seconds(pact, num_seconds):
    timeout = num_seconds + 1
    time_before = flux.current_timeline.time()
    group = PactGroup([pact], timeout_seconds=num_seconds)
    with pytest.raises(TimeoutExpired):
        group.wait(timeout_seconds=timeout)
    assert timeout == flux.current_timeline.time() - time_before


def test_group_and_pact_with_duration(pact_duration, num_seconds):
    group_duration = num_seconds + 10
    time_before = flux.current_timeline.time()
    group = PactGroup([pact_duration], timeout_seconds=group_duration)
    with pytest.raises(TimeoutExpired):
        group.wait()
    assert group_duration == flux.current_timeline.time() - time_before


def test_group_without_absorb(pred1, pred2, checkpoint, checkpoint1, checkpoint2, checkpoint3):
    p1 = Pact('a').until(pred1).lastly(checkpoint).then(checkpoint1)
    p2 = Pact('b').until(pred2).then(checkpoint2).lastly(checkpoint3)
    group = p1 + p2
    assert not checkpoint1.called
    pred1.satisfy()
    assert not group.poll()
    assert checkpoint.called
    assert checkpoint1.called
    assert not checkpoint2.called
    assert not checkpoint3.called
    pred2.satisfy()
    assert group.poll() and group.is_finished()
    assert checkpoint2.called
    assert checkpoint3.called


def test_group_with_absorb(pred1, pred2, checkpoint, checkpoint1, checkpoint2, checkpoint3):
    # pylint: disable=protected-access
    p1 = Pact('a').until(pred1).lastly(checkpoint).then(checkpoint1)
    p2 = Pact('b').until(pred2).then(checkpoint2).lastly(checkpoint3)
    group = PactGroup()
    group.add(p1, absorb=True)
    group.add(p2, absorb=True)
    assert not p1._then
    assert not p1._lastly
    assert not p2._then
    assert not p2._lastly
    assert not checkpoint.called
    assert not checkpoint1.called
    pred1.satisfy()
    assert not group.poll() and not group.is_finished()
    assert not checkpoint.called
    assert not checkpoint1.called
    assert not checkpoint2.called
    assert not checkpoint3.called
    pred2.satisfy()
    assert group.poll() and group.is_finished()
    assert checkpoint.called
    assert checkpoint1.called
    assert checkpoint2.called
    assert checkpoint3.called


def test_abosrbing_group_not_implemented():
    group = PactGroup()
    group2 = PactGroup()
    with pytest.raises(NotImplementedError):
        group.add(group2, absorb=True)


def test_iterating_empty_pact_group():
    assert list(PactGroup()) == []


@pytest.mark.parametrize('satisfy_first', [True, False])
def test_iterating_nonempty_pact_group(pred1, pred2, satisfy_first):
    g = PactGroup()
    p1 = Pact('1').until(pred1)
    p2 = Pact('2').until(pred2)
    g.add(p1)
    g.add(p2)

    assert list(g) == [p1, p2]

    if satisfy_first:
        pred1.satisfy()
    else:
        pred2.satisfy()

    g.poll()
    assert sorted(g, key=str) == [p1, p2]



@pytest.fixture
def timed_group(absorb, timed_pact):
    returned = PactGroup()
    returned.add(timed_pact, absorb=absorb)
    return returned


@pytest.fixture
def timed_pact(timed_predicate_factory):
    return Pact('delayed').until(timed_predicate_factory())


@pytest.fixture(params=[True, False])
def absorb(request):
    return request.param
