import os
import shutil
import PyInstaller.__main__

os.system(
    '"' + os.path.join("E:\\", "program files", "VisualStudio", "Msbuild", "Current", "BIn", "MSBuild.exe") + '"' +
    " ./src/find_handle/find_handle.sln /p:Configuration=Release")
shutil.copyfile(os.path.join(".", "src", "find_handle", "x64", "Release", "find_handle.exe"),
                os.path.join(".", "bin", "find_handle.exe"))

PyInstaller.__main__.run([
    '--windowed',
    '--clean',
    '--name', 'Uexit',
    '--onefile',
    '--add-data=res/main.ui;./res',
    '--add-data=bin/find_handle.exe;./bin',
    '--add-data=res/icon.ico;./res',
    '--add-data=res/CascadiaMono.ttf;./res',
    '--add-data=res/simhei.ttf;./res',
    '--icon=res/icon.ico',
    os.path.join("src", "main.py")
])
