import shutil
import sys
from pathlib import Path

import openpyxl
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from sfcr.pipeline import analyse, load_config  # noqa: E402


@pytest.fixture(scope="session")
def cfg():
    return load_config(ROOT / "config")


@pytest.fixture
def inputs(tmp_path):
    """A copy of date/; tests break the copy of registru_2025.xlsx, never the original."""
    for p in (ROOT / "date").iterdir():
        if p.is_file() and not p.name.startswith("."):
            shutil.copy(p, tmp_path / p.name)
    return tmp_path


@pytest.fixture
def run(inputs, cfg):
    """run(change) edits the workbook copy with openpyxl, then analyses 2025."""
    def _run(change=None, config=None):
        if change is not None:
            path = inputs / "registru_2025.xlsx"
            wb = openpyxl.load_workbook(path)
            change(wb)
            wb.save(path)
        return analyse(2025, inputs, config or cfg)
    return _run
