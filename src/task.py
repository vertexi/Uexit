import psutil
from PyQt5.QtCore import pyqtSignal, QObject, pyqtBoundSignal
from ui import MyTreeWidgetItem


class Tasks(QObject):
    send_kill_status_message: pyqtBoundSignal
    send_kill_status_message = pyqtSignal(str)
    clean_killed_tree_item: pyqtBoundSignal
    clean_killed_tree_item = pyqtSignal(MyTreeWidgetItem)

    def __init__(self):
        super(Tasks, self).__init__()

    def kill(self, tree_widget_item_list: list):
        for tree_widget_item in tree_widget_item_list:
            attempt = 20
            pid_num = int(tree_widget_item.datum)
            name = ""
            try:
                process = psutil.Process(pid_num)
                name = process.name()
            except Exception as e:
                self.send_kill_status_message.emit(f"failed: kill {name}({pid_num}) process failed.{e}")
                return
            while psutil.pid_exists(pid_num):
                try:
                    process.kill()
                except Exception as e:
                    self.send_kill_status_message.emit(f"failed: kill {name}({pid_num}) process failed.{e}")
                    return
                else:
                    attempt = attempt - 1
                    if attempt < 0:
                        self.send_kill_status_message.emit(f"failed: kill {name}({pid_num}) process failed.")
                        return
            self.send_kill_status_message.emit(f"success: kill {name}({pid_num}) process finished.")
            self.clean_killed_tree_item.emit(tree_widget_item)
