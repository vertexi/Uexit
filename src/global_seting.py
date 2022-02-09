import os
import sys

icon_file = ""
exec_file = ""
ui_file = ""
font_cascadia_file = ""
font_simhei_file = ""

"""
build command:
pyinstaller.exe --windowed --clean --name "Uexit" --onefile `
    --add-data="res/main.ui;./res" `
    --add-data="bin/find_handle.exe;./bin" `
    --add-data="res/icon.ico;./res" `
    --add-data="res/CascadiaMono.ttf;./res" `
    --add-data="res/simhei.ttf;./res" `
    --icon=res/icon.ico `
    src/main.py
"""


def resource_path(relative_path):
    bundle_dir = getattr(sys, '_MEIPASS', os.path.abspath(os.path.dirname(__file__)))
    file_path = os.path.abspath(os.path.join(bundle_dir, relative_path))
    return file_path


def set_path(debug: bool):
    global icon_file
    global exec_file
    global ui_file
    global font_cascadia_file
    global font_simhei_file
    if debug:
        icon_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'icon.ico'))
        exec_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', "bin", "find_handle.exe"))
        ui_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'main.ui'))
        font_cascadia_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'CascadiaMono.ttf'))
        font_simhei_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'simhei.ttf'))
    else:
        icon_file = resource_path(os.path.join("res", "icon.ico"))
        exec_file = resource_path(os.path.join("bin", "find_handle.exe"))
        ui_file = resource_path(os.path.join("res", "main.ui"))
        font_cascadia_file = resource_path(os.path.join('res', 'CascadiaMono.ttf'))
        font_simhei_file = resource_path(os.path.join('res', 'simhei.ttf'))
