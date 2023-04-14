import pytest

from golident import Golident


@pytest.fixture(scope="module")
def golident_instance():
    return Golident("asdf", size=32, iterations=80, num_colors=5)


def test_identicon_array(golident_instance):
    assert golident_instance.identicon_array[0][0] == 178.5
