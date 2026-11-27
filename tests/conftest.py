import sys
import winreg
from collections.abc import Iterator
from pathlib import Path

import pytest

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from libs.registry import RegistryDict  # noqa: E402

# Throwaway branch under the current user's hive - nothing outside it is touched.
SCRATCH_BRANCH = r"Software\win_reg_editing_tests"


def _delete_tree(root: int, branch: str) -> None:
    """Remove a key and all its subkeys with plain winreg, independent of the code under test."""
    try:
        with winreg.OpenKey(root, branch, 0, winreg.KEY_READ) as key:
            subkeys = []
            while True:
                try:
                    subkeys.append(winreg.EnumKey(key, len(subkeys)))
                except OSError:
                    break
    except FileNotFoundError:
        return
    for sub in subkeys:
        _delete_tree(root, f"{branch}\\{sub}")
    winreg.DeleteKey(root, branch)


@pytest.fixture
def scratch_branch() -> Iterator[str]:
    """A registry branch that doesn't exist at the start of the test and is removed afterwards."""
    _delete_tree(winreg.HKEY_CURRENT_USER, SCRATCH_BRANCH)
    yield SCRATCH_BRANCH
    _delete_tree(winreg.HKEY_CURRENT_USER, SCRATCH_BRANCH)


@pytest.fixture
def scratch(scratch_branch: str) -> RegistryDict:
    """RegistryDict for the scratch branch, already created."""
    winreg.CreateKey(winreg.HKEY_CURRENT_USER, scratch_branch).Close()
    return RegistryDict("HKCU", scratch_branch)


def read_raw(branch: str, name: str) -> tuple:
    """(value, type) straight from winreg, to check what was really written."""
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, branch) as key:
        return winreg.QueryValueEx(key, name)
