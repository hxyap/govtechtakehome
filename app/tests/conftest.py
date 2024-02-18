import sys
from pathlib import Path
import os
import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent))

@pytest.fixture(autouse=True)
def setup_test_env():
    os.environ["TEST_ENV"] = "True"
    yield
    del os.environ["TEST_ENV"]
