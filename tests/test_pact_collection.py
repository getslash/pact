import pytest
import flux
from pact import Pact, PactChain, PactGroup
from waiting.exceptions import TimeoutExpired

# pylint: disable=redefined-outer-name


@pytest.mark.parametrize('collection_type', [PactGroup, PactChain])
@pytest.mark.parametrize('is_adding', [True, False])
def test_collection_iadd_pact(collection_type, is_adding):
    collection = collection_type()
    if is_adding:
        p1 = collection_type(pacts=[Pact('c'), Pact('d')])
    else:
        p1 = Pact('c')
    collection += p1
    assert collection._pacts[-1] is p1  # pylint: disable=protected-access


@pytest.mark.parametrize('collection_type', [PactGroup, PactChain])
def test_empty_collection(collection_type):
    collection = collection_type()
    assert collection._pacts == [] # pylint: disable=protected-access
    assert list(collection) == []


@pytest.mark.parametrize('collection_type', [PactGroup, PactChain])
def test_collection_with_duration(collection_type, pact, num_seconds):
    time_before = flux.current_timeline.time()
    collection = collection_type([pact], timeout_seconds=num_seconds)
    with pytest.raises(TimeoutExpired):
        collection.wait()
    assert num_seconds == flux.current_timeline.time() - time_before


@pytest.mark.parametrize('collection_type', [PactGroup, PactChain])
def test_chain_with_duration_wait_timeout_seconds(collection_type, pact, num_seconds):
    timeout = num_seconds + 1
    time_before = flux.current_timeline.time()
    chain = collection_type([pact], timeout_seconds=num_seconds)
    with pytest.raises(TimeoutExpired):
        chain.wait(timeout_seconds=timeout)
    assert timeout == flux.current_timeline.time() - time_before


@pytest.mark.parametrize('collection_type', [PactGroup, PactChain])
def test_chain_and_pact_with_duration(collection_type, pact_duration, num_seconds):
    chain_duration = num_seconds + 10
    time_before = flux.current_timeline.time()
    chain = collection_type([pact_duration], timeout_seconds=chain_duration)
    with pytest.raises(TimeoutExpired):
        chain.wait()
    assert chain_duration == flux.current_timeline.time() - time_before


@pytest.mark.parametrize('collection_type', [PactGroup, PactChain])
@pytest.mark.parametrize('satisfy_first', [True, False])
def test_iterating_nonempty_pact_group(collection_type, pred1, pred2, satisfy_first):
    g = collection_type()
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


@pytest.fixture
def timed_group(collection_type, absorb, timed_pact):
    returned = collection_type()
    if collection_type == PactGroup:
        returned.add(timed_pact)
    else:
        returned.add(timed_pact)
    return returned


@pytest.fixture
def timed_pact(timed_predicate_factory):
    return Pact('delayed').until(timed_predicate_factory())
