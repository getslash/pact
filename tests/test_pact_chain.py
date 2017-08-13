import pytest
import flux
from pact import Pact, PactChain, PactGroup
from waiting.exceptions import TimeoutExpired

# pylint: disable=redefined-outer-name

def test_chain(pred1, pred2, checkpoint, checkpoint1, checkpoint2, checkpoint3):
    p1 = Pact('a').until(pred1).lastly(checkpoint).then(checkpoint1)
    p2 = Pact('b').until(pred2).then(checkpoint2).lastly(checkpoint3)
    chain = PactChain([p1, p2])
    assert not checkpoint1.called
    pred1.satisfy()
    assert not chain.poll() and not chain.is_finished()
    assert pred1.called
    assert not pred2.called
    assert checkpoint.called
    assert checkpoint1.called
    assert not checkpoint2.called
    assert not checkpoint3.called
    pred2.satisfy()
    assert chain.poll() and chain.is_finished()
    assert checkpoint2.called
    assert checkpoint3.called


def test_chain_order(pred1, pred2, checkpoint, checkpoint1, checkpoint2, checkpoint3):
    p1 = Pact('a').until(pred1).lastly(checkpoint).then(checkpoint1)
    p2 = Pact('b').until(pred2).then(checkpoint2).lastly(checkpoint3)
    chain = PactChain([p1, p2])
    assert not checkpoint1.called
    pred2.satisfy()
    assert not chain.poll() and not chain.is_finished()
    assert pred1.called
    assert not pred2.called
    assert not checkpoint.called
    assert not checkpoint1.called
    assert not checkpoint2.called
    assert not checkpoint3.called
    pred1.satisfy()
    chain.poll()
    assert chain.poll() and chain.is_finished()
    assert checkpoint.called
    assert checkpoint1.called
    assert checkpoint2.called
    assert checkpoint3.called

@pytest.mark.parametrize('collection_type', [PactGroup, PactChain])
def test_chain_collections(collection_type, pred1, pred2, checkpoint, checkpoint1, checkpoint2, checkpoint3):
    p1 = Pact('a').until(pred1).lastly(checkpoint).then(checkpoint1)
    p2 = Pact('b').until(pred2).then(checkpoint2).lastly(checkpoint3)
    c1 = collection_type([p1])
    c2 = collection_type([p2])
    chain = PactChain([c1, c2])
    assert not checkpoint1.called
    pred1.satisfy()
    assert not chain.poll() and not chain.is_finished()
    assert checkpoint.called
    assert checkpoint1.called
    assert not checkpoint2.called
    assert not checkpoint3.called
    pred2.satisfy()
    assert chain.poll() and chain.is_finished()
    assert checkpoint2.called
    assert checkpoint3.called
