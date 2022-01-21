import sys
from subprocess import PIPE, Popen
from proc_parse import CollectProcess
from ui import MainWindow
from PyQt5.QtWidgets import QApplication

sys.path.append(".")
ON_POSIX = 'posix' in sys.builtin_module_names

if __name__ == '__main__':
    process = Popen(["./handle64.exe", "E:\\"], stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
    collect_proc = CollectProcess(process.stdout)

    app = QApplication(sys.argv)
    main_window = MainWindow()
    app.exec_()
