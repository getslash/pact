import pytest
import flux
from pact import Pact, PactGroup, PactChain
from waiting.exceptions import TimeoutExpired

# pylint: disable=redefined-outer-name

def test_group_without_absorb(pred1, pred2, checkpoint, checkpoint1, checkpoint2, checkpoint3):
    p1 = Pact('a').until(pred1).lastly(checkpoint).then(checkpoint1)
    p2 = Pact('b').until(pred2).then(checkpoint2).lastly(checkpoint3)
    group = p1 + p2
    assert not checkpoint1.called
    pred1.satisfy()
    assert not group.poll()
    assert pred1.called
    assert pred2.called
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


@pytest.mark.parametrize('absorbed_type', [PactGroup, PactChain])
def test_abosrbing_group_or_chain_not_implemented(absorbed_type):
    group = PactGroup()
    absorbed = absorbed_type()
    with pytest.raises(NotImplementedError):
        group.add(absorbed, absorb=True)
