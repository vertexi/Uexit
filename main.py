import sys
from threading import Thread
from queue import Queue, Empty
from subprocess import PIPE, Popen
from proc_parse import collect_proc

ON_POSIX = 'posix' in sys.builtin_module_names


if __name__ == '__main__':
    process = Popen(["./handle64.exe", "E:\\"], stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
    processes = []
    proc_parse_proc = Thread(target=collect_proc, args=(process.stdout, processes))
    proc_parse_proc.start()
