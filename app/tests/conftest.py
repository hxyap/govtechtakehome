import sys
from pathlib import Path
import os
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ["TEST_ENV"] = "True"
    # Add any other test setup steps here
    yield
    # Add teardown steps here if necessary
    del os.environ["TEST_ENV"]
