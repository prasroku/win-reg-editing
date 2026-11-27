"""The screensaver example must put the user's original settings back, not blank them."""

import pytest

from libs.registry import RegistryDict
from src import test_screen_saver as screen_saver

SCR = r"C:\Windows\system32\Mystify.scr"


def test_apply_settings_when_called_writes_all_values_and_returns_originals(scratch: RegistryDict) -> None:
    scratch["ScreenSaveTimeOut"] = "600"

    originals = screen_saver.apply_settings(scratch, SCR)

    assert scratch["ScreenSaveActive"] == "1"
    assert scratch["ScreenSaverIsSecure"] == "1"
    assert scratch["ScreenSaveTimeOut"] == "120"
    assert scratch["SCRNSAVE.EXE"] == SCR
    assert originals["ScreenSaveTimeOut"] == "600"
    assert originals["SCRNSAVE.EXE"] is None


def test_restore_settings_when_values_existed_puts_them_back_and_removes_new_ones(scratch: RegistryDict) -> None:
    scratch["ScreenSaveTimeOut"] = "600"
    scratch["ScreenSaveActive"] = "0"
    originals = screen_saver.apply_settings(scratch, SCR)

    screen_saver.restore_settings(scratch, originals)

    assert scratch["ScreenSaveTimeOut"] == "600"
    assert scratch["ScreenSaveActive"] == "0"
    assert "SCRNSAVE.EXE" not in scratch
    assert "ScreenSaverIsSecure" not in scratch


def test_temporary_screensaver_when_block_raises_still_restores(scratch: RegistryDict) -> None:
    scratch["ScreenSaveTimeOut"] = "600"

    with pytest.raises(RuntimeError):
        with screen_saver.temporary_screensaver(scratch, SCR):
            assert scratch["ScreenSaveTimeOut"] == "120"
            raise RuntimeError("boom")

    assert scratch["ScreenSaveTimeOut"] == "600"
    assert "SCRNSAVE.EXE" not in scratch


def test_pick_screensaver_when_none_installed_raises_clear_error() -> None:
    with pytest.raises(FileNotFoundError, match="No screensavers"):
        screen_saver.pick_screensaver(pattern=r"C:\definitely\not\here\*.scr")


def test_pick_screensaver_when_installed_returns_one_of_them() -> None:
    scr = screen_saver.pick_screensaver()

    assert scr.lower().endswith(".scr")
