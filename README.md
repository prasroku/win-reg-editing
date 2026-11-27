# win_reg_editing

A small Python wrapper for reading and editing keys in the Windows registry, plus an example that sets a random Windows screensaver.

## Usage

`RegistryDict` treats a registry branch like a dictionary:

```python
from libs.registry import RegistryDict

desktop = RegistryDict("HKCU", r"Control Panel\Desktop")

desktop["ScreenSaveTimeOut"] = "120"    # str -> REG_SZ, int -> REG_DWORD, list -> REG_MULTI_SZ
print(desktop["ScreenSaveTimeOut"])     # missing values raise KeyError
print(desktop.get("Missing", "default"))
print("ScreenSaveActive" in desktop)
del desktop["SomeValue"]

desktop.items()        # all (name, value) pairs
desktop.subkeys()      # direct child branches
desktop.exists(), desktop.create(), desktop.wipe()

RegistryDict.wow64_32("HKLM", r"Software\Vendor")   # 32-bit view (WOW6432Node)
```

Hives: `HKLM`, `HKCU`, `HKCR`, `HKCC`, `HKU` (or their full `HKEY_...` names). Writing under `HKLM` needs an elevated terminal.

### Screensaver example

`src/test_screen_saver.py` picks a random `.scr` from `C:\Windows\system32` and enables it with a 2-minute timeout and a password on resume.

```
.venv\Scripts\python.exe src\test_screen_saver.py
```

This changes your real screensaver settings and prints the previous values so you can put them back. To apply the settings only temporarily, use the context manager, which restores the originals when the block ends (even on an error):

```python
from libs.registry import RegistryDict
from src.test_screen_saver import pick_screensaver, temporary_screensaver

with temporary_screensaver(RegistryDict("HKCU", r"Control Panel\Desktop"), pick_screensaver()):
    ...  # screensaver is active here
```

## Setup

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## Tests

```
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.venv\Scripts\python.exe -m pytest tests
```

Windows only. The tests use a throwaway key, `HKCU\Software\win_reg_editing_tests`, and delete it afterwards. Nothing else in the registry is touched.
