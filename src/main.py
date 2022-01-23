import sys
from PyQt5.QtWidgets import QApplication
from ui import MainWindow

sys.path.append(".")
ON_POSIX = 'posix' in sys.builtin_module_names

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()  # initialize main window
    app.exec_()  # run
