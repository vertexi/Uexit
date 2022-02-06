import os
import sys


def resource_path(relative_path):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    file_path = os.path.abspath(os.path.join(bundle_dir, relative_path))
    return file_path


"""
build command:
pyinstaller.exe --windowed --clean --name "Uexit" --onefile `
    --add-data="res/main.ui;./res" `
    --add-data="bin/find_handle.exe;./bin" `
    --add-data="res/icon.ico;./res" `
    --icon=res/icon.ico `
    src/main.py
"""
DEBUG = True
if DEBUG:
    icon_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'icon.ico'))
    exec_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "bin", "find_handle.exe"))
    ui_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'main.ui'))
else:
    icon_file = resource_path(os.path.join("res", "icon.ico"))
    exec_file = resource_path(os.path.join("bin", "find_handle.exe"))
    ui_file = resource_path(os.path.join("res", "main.ui"))
