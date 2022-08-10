# Copyright (C) 2022 James Ravindran
# SPDX-License-Identifier: CC0-1.0

from pathlib import Path
import platform

# https://stackoverflow.com/a/48706260
def get_music_path():
    if platform.system() == "Windows":
        import winreg
        sub_key = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders"
        downloads_guid = "My Music"
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, sub_key) as key:
            location = winreg.QueryValueEx(key, downloads_guid)[0]
        return Path(location)
    else:
        return Path.home() / "Music"
