import sys
from subprocess import PIPE, Popen
from proc_parse import CollectProcess
from ui import MainWindow
from PyQt5.QtWidgets import QApplication

sys.path.append(".")
ON_POSIX = 'posix' in sys.builtin_module_names

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()

    collect_proc = CollectProcess()
    collect_proc.update_tree_signal.connect(main_window.process_tree.build_process_tree)
    main_window.file_path_input.start_proc_signal.connect(collect_proc.start_process)

    app.exec_()
