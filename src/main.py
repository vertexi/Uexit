import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QIcon
from ui import MainWindow
import global_seting

sys.path.append(".")
# make a custom application id
try:
    # Include in try/except block if you're also targeting Mac/Linux
    from PyQt5.QtWinExtras import QtWin
    QtWin.setCurrentProcessExplicitAppUserModelID('com.yhsxz.Uexit.1.0')
except ImportError:
    pass

if __name__ == '__main__':
    app = QApplication(sys.argv)  # initialize qt app
    app.setWindowIcon(QIcon(QPixmap(global_seting.icon_file)))  # make icon
    main_window = MainWindow()  # initialize main window
    app.exec_()  # run
