"""Enable a random Windows screensaver with a 2-minute timeout.

Run directly to apply the settings (the previous values are printed so you can
put them back), or use `temporary_screensaver()` to apply them for the length of
a `with` block and restore the originals afterwards.
"""

import contextlib
import glob
import random
import sys
from collections.abc import Iterator
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent.parent))

from libs.registry import RegistryDict  # noqa: E402

DESKTOP_BRANCH = r"Control Panel\Desktop"
SCREENSAVER_GLOB = r"C:\Windows\system32\*.scr"


def desired_settings(screensaver: str) -> dict[str, str]:
    return {
        "ScreenSaveActive": "1",
        "ScreenSaverIsSecure": "1",
        "ScreenSaveTimeOut": "120",
        "SCRNSAVE.EXE": screensaver,
    }


def pick_screensaver(pattern: str = SCREENSAVER_GLOB) -> str:
    candidates = glob.glob(pattern)
    if not candidates:
        raise FileNotFoundError(f"No screensavers found matching {pattern}")
    return random.choice(candidates)


def apply_settings(reg: RegistryDict, screensaver: str) -> dict[str, str | None]:
    """Write the screensaver settings and return the previous values (None where a value didn't exist)."""
    settings = desired_settings(screensaver)
    if not reg.exists():
        reg.create()
    originals = {name: reg.get(name) for name in settings}
    for name, value in settings.items():
        reg.setitem(name, value)
    return originals


def restore_settings(reg: RegistryDict, originals: dict[str, str | None]) -> None:
    """Put back the values `apply_settings` returned; values that didn't exist before are removed."""
    for name, value in originals.items():
        if value is None:
            with contextlib.suppress(KeyError):
                del reg[name]
        else:
            reg.setitem(name, value)


@contextlib.contextmanager
def temporary_screensaver(reg: RegistryDict, screensaver: str) -> Iterator[str]:
    originals = apply_settings(reg, screensaver)
    try:
        yield screensaver
    finally:
        restore_settings(reg, originals)


def main() -> None:
    reg = RegistryDict("HKCU", DESKTOP_BRANCH)
    screensaver = pick_screensaver()
    originals = apply_settings(reg, screensaver)
    print(f"Screensaver set to {screensaver} (2-minute timeout, password on resume).")
    print("Previous values:")
    for name, value in originals.items():
        print(f"  {name} = {value!r}")
    print("Windows may need you to sign out and back in before the change takes effect.")


if __name__ == "__main__":
    main()
