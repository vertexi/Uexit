import sys
import _io
from PyQt5.QtCore import pyqtSignal, QObject, pyqtBoundSignal
from threading import Thread, Lock
from subprocess import PIPE, Popen
import time
import psutil
import global_seting

ON_POSIX = 'posix' in sys.builtin_module_names


class MyThreadParseProc(Thread):
    def __init__(self, str_reader: _io.BufferedReader, update_signal: pyqtBoundSignal,
                 complete_signal: pyqtBoundSignal):
        """
        process the string buffer send main_windows's tree widget update
        :param str_reader: buffer string
        :param update_signal:
        """
        super(MyThreadParseProc, self).__init__()
        self.mutex = Lock()
        self.stop_status = False
        self.update_tree_signal = update_signal
        self.complete_signal = complete_signal
        self.str_reader = str_reader

    def my_stop(self):
        self.stop_status = True

    def my_start(self):
        self.stop_status = False
        self.start()

    def run(self):
        # read handle.exe output stream send to proc_parser get process info
        for line in iter(self.str_reader.readline, b''):
            # stop code condition
            self.mutex.acquire()
            try:
                if self.stop_status:
                    break
            finally:
                self.mutex.release()
            # parse the input stream
            parsed = proc_parser(line)
            self.update_tree_signal.emit(parsed)
        self.complete_signal.emit("Search end")


class MyThreadFindExe(Thread):
    def __init__(self, file_path: str, update_signal: pyqtBoundSignal):
        super(MyThreadFindExe, self).__init__()
        self.mutex = Lock()
        self.stop_status = False
        self.update_tree_signal = update_signal
        self.file_path = file_path

    def my_stop(self):
        self.stop_status = True

    def my_start(self):
        self.stop_status = False
        self.start()

    def run(self):
        for p in psutil.process_iter(['name', 'pid', "exe"]):
            if p.info["exe"]:
                if p.info["exe"].startswith(self.file_path):
                    result = list([p.info["name"], str(p.info["pid"]), "", p.info["exe"]])
                    self.update_tree_signal.emit(result)
            # stop code condition
            self.mutex.acquire()
            try:
                if self.stop_status:
                    return
            finally:
                self.mutex.release()


class CollectProcess(QObject):
    update_tree_signal: pyqtBoundSignal
    update_tree_signal = pyqtSignal(list)
    complete_signal: pyqtBoundSignal
    complete_signal = pyqtSignal(str)

    process: Popen
    proc_parse_proc: MyThreadParseProc

    def __init__(self, arg_list: list):
        super().__init__()
        self.process_tree = {"proc_names": {}, "open_files": {}}  # process name dict, process open file dict
        # for windows, create a process without a console
        self.process = Popen([global_seting.exec_file] + arg_list,
                             stdout=PIPE, bufsize=1, close_fds=ON_POSIX, creationflags=0x00000008)
        str_reader = self.process.stdout  # get string stream from handle.exe
        # create a thread to parse the buffer string
        self.proc_parse_proc = MyThreadParseProc(str_reader, self.update_tree_signal, self.complete_signal)
        # create a thread to find the executable path include the file_path
        self.find_exe_proc = MyThreadFindExe(arg_list[-1], self.update_tree_signal)

    def start_process(self):
        self.proc_parse_proc.my_start()
        self.find_exe_proc.my_start()

    def kill_exist_process(self):
        if self.process is None:
            return
        else:
            if self.process.poll() is None:
                self.process.kill()

        if self.proc_parse_proc:
            self.proc_parse_proc.my_stop()
        if self.find_exe_proc:
            self.find_exe_proc.my_stop()
        time.sleep(0.1)


def proc_parser(process_str: bytes):
    """
    split process_str to process_name pid and file_name
    Example string
    jcef_helper.exe    pid: 25532  type: File           308: E:\\Program Files\\percent.pak
    :param process_str:
    :return: list(process_name+pid, file_name)
    """
    process_str = process_str.decode('utf-8')  # decode binary to string
    process_str = process_str.split("\t")  # split string

    pid = process_str[1][4:-2].strip()  # get pid
    file_name = process_str[0][5:]  # get open file name
    process_name = ""
    proc_exe = ""

    # try to get process name and exec path
    try:
        proc = psutil.Process(int(pid))
        process_name = proc.name()
        proc_exe = proc.exe()
    except:
        pass

    return list([process_name, pid, file_name, proc_exe])
