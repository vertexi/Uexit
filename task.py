import psutil
from PyQt5.QtCore import QObject


class Tasks(QObject):
    def __init__(self):
        super(Tasks, self).__init__()

    def kill(self, pid: str):
        psutil.Process(int(pid)).kill()
