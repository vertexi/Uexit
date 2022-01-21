import _io

def proc_parser(process_str: bytes):
    """
    split process_str to process_name pid and file_name
    Example string
    jcef_helper.exe    pid: 25532  type: File           308: E:\Program Files\percent.pak
    :param process_str:
    :return: list(process_name, pid, file_name)
    """
    process_str = process_str.decode('utf-8')  # decode binary to string
    # print(process_str)
    process_str = process_str.split(": ")  # split string

    pid_pos = process_str[0].rfind("pid")  # find pid string position
    process_name = process_str[0][:pid_pos].strip() # get process name

    type_pos = process_str[1].rfind("type")  # find type string position
    pid = process_str[1][:type_pos].strip()  # get pid

    file_name = process_str[3].strip()

    return list([process_name, pid, file_name])


def collect_proc(str_reader: _io.BufferedReader, processes: list):
    for _ in range(5):
        str_reader.readline()
    for line in iter(str_reader.readline, b''):
        processes.append(proc_parser(line))

