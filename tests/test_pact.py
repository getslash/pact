import pact

import pytest


@pytest.mark.parametrize('reprify', [repr, str])
def test_str_repr(reprify):
    msg = 'Some message here'
    p = pact.Pact(msg)
    assert msg in reprify(p)
