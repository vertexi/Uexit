import sys
from subprocess import PIPE, Popen
from proc_parse import CollectProcess

sys.path.append(".")
ON_POSIX = 'posix' in sys.builtin_module_names

if __name__ == '__main__':
    process = Popen(["./handle64.exe", "E:\\"], stdout=PIPE, bufsize=1, close_fds=ON_POSIX)
    collect_proc = CollectProcess(process.stdout)

