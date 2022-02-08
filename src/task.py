import psutil
from PyQt5.QtCore import pyqtSignal, QObject, pyqtBoundSignal
from ui import MyTreeWidgetItem
from subprocess import Popen
import global_seting
import sys


ON_POSIX = 'posix' in sys.builtin_module_names


class Tasks(QObject):
    process: Popen

    send_kill_status_message: pyqtBoundSignal
    send_kill_status_message = pyqtSignal(str)
    clean_killed_tree_item: pyqtBoundSignal
    clean_killed_tree_item = pyqtSignal(MyTreeWidgetItem)

    def __init__(self):
        super(Tasks, self).__init__()
        self.process = None

    def kill_process(self, tree_widget_item_list: list):
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

    def kill_single_handle(self, handle_info: list):
        arg_list = ["-close", str(int(handle_info[0])), handle_info[1].text(0)]
        self.stop_self_process()
        self.process = Popen([global_seting.exec_file] + arg_list, close_fds=ON_POSIX, creationflags=0x00000008)
        return_code = self.process.wait(timeout=1)
        if return_code is not None:
            return_code = int(return_code)
            if return_code == 0:
                self.clean_killed_tree_item.emit(handle_info[1])
                self.send_kill_status_message.emit(f"success: close {handle_info[1].text(0)}) process finished.")
                return
        self.send_kill_status_message.emit(f"failed: close {handle_info[1].text(0)}) process failed.")

    def kill_handle(self, handle_list: list):
        # handle_list [[pid_string: str, file path: MyTreeWidgetItem], ...]
        for handle in handle_list:
            self.kill_single_handle(handle)

    def stop_self_process(self):
        if self.process:
            if self.process.poll() is None:
                self.process.kill()

