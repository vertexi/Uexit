from PyQt5 import uic
from PyQt5.QtGui import QGuiApplication, QFontMetrics
from PyQt5.QtWidgets import QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, \
    QPushButton, QLineEdit, QHBoxLayout, QWidget, QHeaderView, QPlainTextEdit, QFileDialog, \
    QDialog, QStackedWidget, QListView, QAction, QMenu
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, pyqtBoundSignal
from proc_parse import CollectProcess
import global_seting
import subprocess


class MyTreeWidgetItem(QTreeWidgetItem):
    datum: str

    def __init__(self, *args, **kwargs):
        super(MyTreeWidgetItem, self).__init__(*args, **kwargs)
        self.datum = ""

    def add_data(self, data):
        self.datum = data


class MyTreeWidget(QTreeWidget):
    start_kill_signal: pyqtBoundSignal
    start_kill_signal = pyqtSignal(list)

    def __init__(self, *args, **kwargs):
        super(MyTreeWidget, self).__init__(*args, **kwargs)
        self.process_tree = {}  # pid:tree_itm
        self.top_items = []
        self.header().setStretchLastSection(False)
        self.header().setSectionResizeMode(QHeaderView.ResizeToContents)
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.AscendingOrder)

        # add context menu
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self._show_context_menu)

    def clear_me(self):
        self.clear()
        self.process_tree = {}  # pid:tree_itm
        self.top_items = []

    def build_process_tree(self, list_: list):
        # list_[0] process_name list_[1] pid list_[2] open file path
        if list_[1] in self.process_tree:
            # create follow child file path item
            path_item = MyTreeWidgetItem()
            path_item.setText(0, list_[2])
            path_item.setFlags(path_item.flags() | Qt.ItemIsUserCheckable)
            path_item.setCheckState(0, Qt.Unchecked)
            self.process_tree[list_[1]].insertChild(0, path_item)
        else:
            # create process_name(PID) top item
            tree_item = MyTreeWidgetItem(self)
            tree_item.setText(0, list_[0] + "(" + list_[1] + ")")
            tree_item.setText(1, list_[3])
            tree_item.add_data(list_[1])
            tree_item.setFlags(tree_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            # create first child file path item
            path_item = MyTreeWidgetItem(tree_item)
            path_item.setText(0, list_[2])
            if list_[2] == "":
                path_item.setHidden(True)
            path_item.setFlags(path_item.flags() | Qt.ItemIsUserCheckable)
            path_item.setCheckState(0, Qt.Unchecked)

            self.process_tree[list_[1]] = tree_item
            self.top_items.append(tree_item)

    def send_to_kill(self):
        kill_list = []
        for i in range(self.topLevelItemCount()):
            if int(self.topLevelItem(i).checkState(0)) > 0:
                kill_list.append(self.topLevelItem(i))
        self.start_kill_signal.emit(kill_list)

    def remove_item(self, item: MyTreeWidgetItem):
        parent = item.parent()
        if parent:
            parent.removeChild(item)
        else:
            self.takeTopLevelItem(self.indexOfTopLevelItem(item))

    # the function to display context menu
    def _show_context_menu(self, position):
        open_file_in_explorer = QAction("Reveal in Explorer")
        open_file_in_explorer.triggered.connect(self.open_file_in_explorer)
        menu = QMenu(self)
        menu.addAction(open_file_in_explorer)
        menu.exec_(self.mapToGlobal(position))

    # the action executed when menu is clicked
    def open_file_in_explorer(self):
        if self.currentItem() in self.top_items:
            file_path = self.currentItem().text(1)
        else:
            file_path = self.currentItem().text(0)
        subprocess.run(f'explorer /select,"{file_path}"')


class MyLineEdit(QLineEdit):
    start_proc_signal: pyqtBoundSignal
    start_proc_signal = pyqtSignal(str)
    textChanged: pyqtBoundSignal

    def __init__(self, *args, **kwargs):
        super(MyLineEdit, self).__init__(*args, **kwargs)
        self.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        self.setText(self.text().replace("/", "\\"))

    def send_to_start_proc(self):
        self.start_proc_signal.emit(str(self.text()))


class MyQFileDialog(QFileDialog):
    selected_filename: str

    def __init__(self, parent=None, caption='', directory='', filter='', initialFilter='', options=None):
        super(MyQFileDialog, self).__init__(parent, caption=caption, directory=directory, filter=filter)
        self.setFileMode(self.ExistingFile)
        if options:
            self.setOptions(options)
        self.setOption(self.DontUseNativeDialog, True)
        if filter and initialFilter:
            self.selectNameFilter(initialFilter)

        # by default, if a directory is opened in file listing mode,
        # QFileDialog.accept() shows the contents of that directory, but we
        # need to be able to "open" directories as we can do with files, so we
        # just override accept() with the default QDialog implementation which
        # will just return exec_()

        self.accept = lambda: QDialog.accept(self)

        # there are many item views in a non-native dialog, but the ones displaying
        # the actual contents are created inside a QStackedWidget; they are a
        # QTreeView and a QListView, and the tree is only used when the
        # viewMode is set to QFileDialog.Details, which is not this case
        self.stackedWidget = self.findChild(QStackedWidget)
        self.view = self.stackedWidget.findChild(QListView)
        self.view.selectionModel().selectionChanged.connect(self.update_text)
        self.lineEdit = self.findChild(QLineEdit)

        # clear the line edit contents whenever the current directory changes
        self.directoryEntered.connect(lambda: self.lineEdit.setText(''))

    def update_text(self):
        # update the contents of the line edit widget with the selected files
        selected = []
        for index in self.view.selectionModel().selectedRows():
            selected.append('"{}"'.format(index.data()))
        self.lineEdit.setText(' '.join(selected))

    def get_selected_files(self):
        self.exec_()
        return self.selectedFiles()


class LineEditDragFileInjector:
    def __init__(self, line_edit, auto_inject=True):
        self.line_edit = line_edit
        if auto_inject:
            self.inject_drag_file()

    def inject_drag_file(self):
        self.line_edit.setDragEnabled(True)
        self.line_edit.dragEnterEvent = self.drag_enter_event
        self.line_edit.dragMoveEvent = self.drag_move_event
        self.line_edit.dropEvent = self.drop_event

    def drag_enter_event(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def drag_move_event(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            event.acceptProposedAction()

    def drop_event(self, event):
        data = event.mimeData()
        urls = data.urls()
        if urls and urls[0].scheme() == 'file':
            # for some reason, this doubles up the intro slash
            filepath = str(urls[0].path())[1:]
            self.line_edit.setText(filepath)


from task import Tasks


class MainWindow(QMainWindow):
    process_tree: QTreeWidget
    verticalLayout_2: QVBoxLayout
    kill_button: QPushButton
    refresh_pushbutton: QPushButton
    status_edit: QPlainTextEdit
    file_path_input: MyLineEdit

    def __init__(self):
        super(MainWindow, self).__init__()

        # Initialize my customized classes
        self.collect_proc = None
        self.kill_task = Tasks()

        # load ui file
        with open(global_seting.ui_file) as ui_file:
            uic.loadUi(ui_file, self)

        # resize window
        self.auto_adj_size()

        # get widgets
        self.central_widget = self.findChild(QWidget, "central_widget")
        self.temp_tree = self.findChild(QTreeWidget, "process_tree")
        self.verticalLayout_2 = self.findChild(QVBoxLayout, "verticalLayout_2")
        self.kill_button = self.findChild(QPushButton, "kill_pushbutton")
        self.tmp_file_path_input = self.findChild(QLineEdit, "file_path_input")
        self.horizontalLayout_2 = self.findChild(QHBoxLayout, "horizontalLayout_2")
        self.refresh_pushbutton = self.findChild(QPushButton, "refresh_pushbutton")
        self.status_edit = self.findChild(QPlainTextEdit, "statusEdit")
        self.file_dialog_button = self.findChild(QPushButton, "file_dialog_button")
        self.file_dialog = MyQFileDialog(self, "Select file to search handles", "", "")

        # replace template widgets to my customized tree widgets
        self.process_tree = MyTreeWidget()
        self.verticalLayout_2.replaceWidget(self.temp_tree, self.process_tree)
        self.file_path_input = MyLineEdit(self.central_widget)
        self.horizontalLayout_2.replaceWidget(self.tmp_file_path_input, self.file_path_input)

        # delete the old tree widgets
        self.verticalLayout_2.removeWidget(self.temp_tree)
        self.temp_tree.deleteLater()
        self.horizontalLayout_2.removeWidget(self.tmp_file_path_input)
        self.tmp_file_path_input.deleteLater()

        self.process_tree.setObjectName("process_tree")
        self.process_tree.setColumnCount(2)
        self.process_tree.setHeaderLabels(["Process_name(PID)", "Exec"])

        self.file_path_input.setText("")
        self.file_path_input.setObjectName("file_path_input")
        self.file_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", "Drop or input file name"))

        LineEditDragFileInjector(self.file_path_input)

        self.set_status_edit_height(1)

        # connect signals and slots
        self.kill_button.clicked.connect(self.process_tree.send_to_kill)
        self.process_tree.start_kill_signal.connect(self.kill_task.kill)

        self.refresh_pushbutton.clicked.connect(self.file_path_input.send_to_start_proc)
        self.file_path_input.start_proc_signal.connect(self.start_collect_process)
        self.refresh_pushbutton.clicked.connect(self.process_tree.clear_me)
        self.file_path_input.editingFinished.connect(self.file_path_input.send_to_start_proc)

        self.kill_task.send_kill_status_message.connect(self.append_status_message)
        self.kill_task.clean_killed_tree_item.connect(self.process_tree.remove_item)

        self.file_dialog_button.clicked.connect(self.file_dialog_button_on_clicked)

        # show app
        self.show()

    def auto_adj_size(self):
        q_rect = QGuiApplication.primaryScreen().geometry()
        self.resize(q_rect.width() / 5, q_rect.height() / 5)

    def start_collect_process(self, file_path: str):
        if self.collect_proc:
            self.collect_proc.kill_exist_process()
        self.collect_proc = CollectProcess(file_path)  # initialize the process collector
        self.collect_proc.update_tree_signal.connect(self.process_tree.build_process_tree)
        self.collect_proc.complete_signal.connect(self.append_status_message)
        self.collect_proc.start_process()
        self.append_status_message("Searching...")

    def append_status_message(self, message: str):
        self.status_edit.appendPlainText(message)
        max_pos = self.status_edit.verticalScrollBar().maximum()
        self.status_edit.verticalScrollBar().setValue(max_pos - 1)

    def set_status_edit_height(self, n_rows: int):
        p_doc = self.status_edit.document()
        font_metrics = QFontMetrics(p_doc.defaultFont())
        margins = self.status_edit.contentsMargins()
        n_height = (font_metrics.lineSpacing() * n_rows
                    + (p_doc.documentMargin() + self.status_edit.frameWidth()) * 2
                    + margins.top() + margins.bottom())
        self.status_edit.setFixedHeight(n_height)

    def file_dialog_button_on_clicked(self):
        self.file_path_input.setText(self.file_dialog.get_selected_files()[0])
