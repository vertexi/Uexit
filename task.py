from PyQt5.QtCore import pyqtSignal, QObject, pyqtBoundSignal


class Tasks(QObject):
    def __init__(self):
        super(Tasks, self).__init__()

    def kill(self):
        print("born to kill")
