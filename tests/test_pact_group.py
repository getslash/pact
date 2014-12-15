import pytest
from pact import Pact


@pytest.mark.parametrize('adding_group', [True, False])
def test_group_iadd_pact(group, adding_group):
    if adding_group:
        p1 = Pact('c') + Pact('d')
    else:
        p1 = Pact('c')
    group += p1
    assert group._pacts[-1] is p1


@pytest.fixture
def group():
    return Pact('a') + Pact('b')
