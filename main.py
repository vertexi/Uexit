import sys
from PyQt5.QtWidgets import QApplication
from proc_parse import CollectProcess
from ui import MainWindow
from task import Tasks

sys.path.append(".")
ON_POSIX = 'posix' in sys.builtin_module_names

if __name__ == '__main__':
    app = QApplication(sys.argv)
    main_window = MainWindow()  # initialize main window
    collect_proc = CollectProcess()  # initialize the process collector
    kill_task = Tasks()

    # connect signals and slots
    collect_proc.update_tree_signal.connect(main_window.process_tree.build_process_tree)
    main_window.file_path_input.start_proc_signal.connect(collect_proc.start_process)
    main_window.process_tree.start_kill_signal.connect(kill_task.kill)

    app.exec_()  # run
