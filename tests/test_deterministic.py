import pytest


@pytest.mark.usefixtures('c')
def test_random_is_deterministic():
    import random
    assert random.randint(1, 100) == 30