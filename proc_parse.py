import sys
import _io
from PyQt5.QtCore import pyqtSignal, QObject, pyqtBoundSignal
from threading import Thread, Lock
from subprocess import PIPE, Popen
import time
import psutil

ON_POSIX = 'posix' in sys.builtin_module_names


class MyThreadParseProc(Thread):
    def __init__(self, str_reader: _io.BufferedReader, update_signal: pyqtBoundSignal):
        super(MyThreadParseProc, self).__init__()
        self.mutex = Lock()
        self.stop_status = False
        self.update_tree_signal = update_signal
        self.str_reader = str_reader

    def my_stop(self):
        self.stop_status = True

    def my_start(self):
        self.stop_status = False
        self.start()

    def run(self):
        """
        :param str_reader: buffer string
        storage parser result list(process_name, pid, file_name) append to self.processes
        """

        # skip the first useless information
        for _ in range(5):
            self.str_reader.readline()

        # read handle.exe output stream send to proc_parser get process info
        for line in iter(self.str_reader.readline, b''):
            # stop code condition
            self.mutex.acquire()
            try:
                if self.stop_status:
                    return
            finally:
                self.mutex.release()
            # parse the input stream
            parsed = proc_parser(line)
            self.update_tree_signal.emit(parsed)


class CollectProcess(QObject):
    update_tree_signal: pyqtBoundSignal
    update_tree_signal = pyqtSignal(list)
    process: Popen
    proc_parse_proc: MyThreadParseProc

    def __init__(self):
        super().__init__()
        self.process_tree = {"proc_names": {}, "open_files": {}}  # process name dict, process open file dict
        self.process = None
        self.proc_parse_proc = None

    def start_process(self, file_path: str):
        self.kill_exist_process()
        self.process_tree = {"proc_names": {}, "open_files": {}}  # process name dict, process open file dict
        self.process = Popen(["./handle64.exe", file_path], stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
        str_reader = self.process.stdout

        # start a thread to parse the buffer string
        self.proc_parse_proc = MyThreadParseProc(str_reader, self.update_tree_signal)
        self.proc_parse_proc.my_start()

    def kill_exist_process(self):
        if self.process is None:
            return
        else:
            if self.process.poll() is None:
                self.process.kill()

        if self.proc_parse_proc:
            self.proc_parse_proc.my_stop()
        time.sleep(0.1)


class MyThreadFindExe(Thread):
    def __init__(self, update_signal: pyqtBoundSignal, target, args):
        super(MyThreadFindExe, self).__init__(target=target, args=args)
        self.mutex = Lock()
        self.stop_status = False
        self.update_tree_signal = update_signal

    def my_stop(self):
        self.stop_status = True

    def find_exe(self, file_path: str):
        for p in psutil.process_iter(['name', 'pid', "exe"]):
            if p.info["exe"]:
                if p.info["exe"].startswith(file_path):
                    result = list([p.info["name"], str(p.info["pid"]), "", p.info["exe"]])
                    self.update_tree_signal.emit(result)


def proc_parser(process_str: bytes):
    """
    split process_str to process_name pid and file_name
    Example string
    jcef_helper.exe    pid: 25532  type: File           308: E:\\Program Files\\percent.pak
    :param process_str:
    :return: list(process_name+pid, file_name)
    """
    process_str = process_str.decode('utf-8')  # decode binary to string
    process_str = process_str.split(": ")  # split string

    pid_pos = process_str[0].rfind("pid")  # find pid string position
    process_name = process_str[0][:pid_pos].strip()  # get process name

    type_pos = process_str[1].rfind("type")  # find type string position
    pid = process_str[1][:type_pos].strip()  # get pid

    file_name = process_str[3].strip()

    proc = psutil.Process(int(pid))
    proc_exe = ""
    try:
        proc_exe = proc.exe()
    except:
        pass

    return list([process_name, pid, file_name, proc_exe])
