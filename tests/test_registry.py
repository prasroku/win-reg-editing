"""RegistryDict / RegKey against a throwaway branch under HKCU (Windows only)."""

import winreg

import pytest
from conftest import read_raw

from libs.registry import (
    RegistryDict,
    RuntimeAndKeyError,
    checkIfBranchExists,
    checkIfKeyExists,
    getRegistryValue,
    setRegistryValue,
)


def test_registry_dict_when_hive_unknown_raises_value_error() -> None:
    with pytest.raises(ValueError):
        RegistryDict("HKXX", r"Software\anything")


def test_exists_when_branch_missing_returns_false(scratch_branch: str) -> None:
    assert RegistryDict("HKCU", scratch_branch).exists() is False


def test_create_when_branch_missing_makes_it_exist(scratch_branch: str) -> None:
    reg = RegistryDict("HKCU", scratch_branch)

    assert reg.create() is True
    assert reg.exists() is True


@pytest.mark.parametrize(
    ("value", "expected_type"),
    [("hello", winreg.REG_SZ), (42, winreg.REG_DWORD), (["a", "b"], winreg.REG_MULTI_SZ)],
    ids=["str", "int", "list"],
)
def test_setitem_when_value_written_reads_back_with_matching_type(
    scratch: RegistryDict, scratch_branch: str, value: object, expected_type: int
) -> None:
    scratch["Value"] = value

    assert scratch["Value"] == value
    assert read_raw(scratch_branch, "Value") == (value, expected_type)


def test_setitem_when_branch_missing_creates_it(scratch_branch: str) -> None:
    reg = RegistryDict("HKCU", scratch_branch)

    reg["Value"] = "x"

    assert reg.exists() is True
    assert reg["Value"] == "x"


def test_getitem_when_value_missing_raises_key_error(scratch: RegistryDict) -> None:
    with pytest.raises(KeyError):
        scratch["Missing"]


def test_getitem_when_branch_missing_raises_key_error(scratch_branch: str) -> None:
    with pytest.raises(RuntimeAndKeyError):
        RegistryDict("HKCU", scratch_branch)["Anything"]


def test_get_when_value_missing_returns_default(scratch: RegistryDict) -> None:
    assert scratch.get("Missing", "fallback") == "fallback"
    assert scratch.get("Missing") is None


def test_contains_when_value_present_or_absent_reports_correctly(scratch: RegistryDict) -> None:
    scratch["Present"] = "yes"

    assert "Present" in scratch
    assert "Absent" not in scratch


def test_delitem_when_value_present_removes_it(scratch: RegistryDict) -> None:
    scratch["Gone"] = 1

    del scratch["Gone"]

    assert "Gone" not in scratch


def test_delitem_when_value_missing_raises_key_error(scratch: RegistryDict) -> None:
    with pytest.raises(KeyError):
        del scratch["Missing"]


def test_items_when_values_written_lists_all_of_them(scratch: RegistryDict) -> None:
    scratch["A"] = "1"
    scratch["B"] = 2

    assert sorted(scratch.items()) == [("A", "1"), ("B", 2)]


def test_subkeys_when_nested_branches_exist_walks_them(scratch: RegistryDict, scratch_branch: str) -> None:
    RegistryDict("HKCU", scratch_branch + r"\child\grandchild").create()

    assert [s.branch for s in scratch.subkeys()] == [scratch_branch + r"\child"]
    assert [s.branch for s in scratch.all_subkeys()] == [
        scratch_branch + r"\child",
        scratch_branch + r"\child\grandchild",
    ]


def test_wipe_when_branch_has_subkeys_removes_everything(scratch: RegistryDict, scratch_branch: str) -> None:
    RegistryDict("HKCU", scratch_branch + r"\child\grandchild").create()
    scratch["Value"] = "x"

    scratch.wipe()

    assert scratch.exists() is False


def test_module_helpers_when_value_set_read_it_back(scratch_branch: str) -> None:
    setRegistryValue("HKCU", scratch_branch, "Helper", "v")

    assert getRegistryValue("HKCU", scratch_branch, "Helper") == "v"
    assert getRegistryValue("HKCU", scratch_branch, "Missing", "d") == "d"
    assert checkIfBranchExists("HKCU", scratch_branch) is True
    assert checkIfKeyExists("HKCU", scratch_branch, "Helper") is True
