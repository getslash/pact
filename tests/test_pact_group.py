import pytest
from pact import Pact, PactGroup


@pytest.mark.parametrize('adding_group', [True, False])
def test_group_iadd_pact(group, adding_group):
    if adding_group:
        p1 = Pact('c') + Pact('d')
    else:
        p1 = Pact('c')
    group += p1
    assert group._pacts[-1] is p1


def test_group_without_absorb_then(pred1, pred2, callback1, callback2):
    p1 = Pact('a').until(pred1).then(callback1)
    p2 = Pact('b').until(pred2).then(callback2)
    group = p1 + p2
    assert not callback1.called
    pred1.satisfy()
    assert not group.finished()
    assert callback1.called
    assert not callback2.called
    pred2.satisfy()
    assert group.finished()
    assert callback2.called


def test_group_with_absorb_then(pred1, pred2, callback1, callback2):
    p1 = Pact('a').until(pred1).then(callback1)
    p2 = Pact('b').until(pred2).then(callback2)
    group = PactGroup()
    group.add(p1, absorb=True)
    group.add(p2, absorb=True)
    assert not p1._then
    assert not p2._then
    assert not callback1.called
    pred1.satisfy()
    assert not group.finished()
    assert not callback1.called
    assert not callback2.called
    pred2.satisfy()
    assert group.finished()
    assert callback1.called
    assert callback2.called


def test_abosrbing_group_not_implemented():
    group = PactGroup()
    group2 = PactGroup()
    with pytest.raises(NotImplementedError):
        group.add(group2, absorb=True)


@pytest.fixture
def group():
    return Pact('a') + Pact('b')
