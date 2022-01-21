import psutil

def inter2():
    pids = psutil.pids()
    for pid in pids:
        if psutil.pid_exists(pid):
            p = psutil.Process(pid)
            try:
                files = p.open_files()
            except psutil.AccessDenied:
                files = []
                pass
            for file in files:
                if file.path.startswith('E:\\'):
                    print("%-5s %-10s %s" % (p.pid, p.exe(), file.path))
                    break


def inter1():
    pids = list()
    for proc in psutil.process_iter(['pid', 'exe', 'open_files']):
        if proc.info['pid'] in pids:
            break
        for file in proc.info['open_files'] or []:
            if file.path.startswith('E:\\'):
                pids.append(proc.pid)
                print("%-5s %-10s %s" % (proc.info['pid'], proc.info['exe'], file.path))
                break

