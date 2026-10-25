import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from uwazi.config import Settings  # noqa: E402
from uwazi.pipeline import run  # noqa: E402
from uwazi.synthetic import generate  # noqa: E402


@pytest.fixture(scope="session")
def raw():
    return generate()


@pytest.fixture(scope="session")
def result(raw):
    return run(raw, Settings(fuzzy_supplier_merge=True))
