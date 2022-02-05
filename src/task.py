import psutil
from PyQt5.QtCore import pyqtSignal, QObject, pyqtBoundSignal
import time

class Tasks(QObject):
    send_kill_status_message: pyqtBoundSignal
    send_kill_status_message = pyqtSignal(str)

    def __init__(self):
        super(Tasks, self).__init__()

    def kill(self, pid: str):
        attempt = 20
        pid_num = int(pid)
        process = psutil.Process(pid_num)
        name = process.name()
        while psutil.pid_exists(pid_num):
            try:
                process.kill()
            except psutil.NoSuchProcess:
                break
            attempt = attempt - 1
            if attempt < 0:
                self.send_kill_status_message.emit(f"failed: kill {name}({pid}) process failed.")
                return
        self.send_kill_status_message.emit(f"success: kill {name}({pid}) process finished.")
