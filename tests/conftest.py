import flux
import pytest


@pytest.fixture(autouse=True, scope='session')
def freeze_flux():
    flux.current_timeline.set_time_factor(0)
