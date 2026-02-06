import os
import pytest

RUN = os.getenv("RUN_INTEGRATION") == "1"

pytestmark = pytest.mark.skipif(not RUN, reason="Integration tests require RUN_INTEGRATION=1")


def test_placeholder_integration():
    assert True
