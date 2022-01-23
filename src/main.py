import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QIcon
from ui import MainWindow
import os

sys.path.append(".")
# make a custom application id
try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    QtWin.setCurrentProcessExplicitAppUserModelID('com.yhsxz.Uexit.1.0')
except ImportError:
    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)

    # make icon
    icon_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'res', 'icon.ico'))
    app.setWindowIcon(QIcon(QPixmap(icon_file)))

    main_window = MainWindow()  # initialize main window
    app.exec_()  # run
