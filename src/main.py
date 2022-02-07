import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPixmap, QIcon, QFont, QFontDatabase
from ui import MainWindow
import global_seting


def font_loader(font_file_path: str):
    id = QFontDatabase.addApplicationFont(font_file_path)
    font_families_name = None
    if id != -1:
        font_families_name = QFontDatabase.applicationFontFamilies(id)
    return font_families_name[0]


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

    font_cascadia = font_loader(global_seting.font_cascadia_file)
    font_simhei = font_loader(global_seting.font_simhei_file)

    app.setFont(QFont(font_cascadia+", "+font_simhei))
    main_window = MainWindow()  # initialize main window

    sys.exit(app.exec_())  # run
