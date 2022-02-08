from PyQt5 import uic
from PyQt5.QtGui import QGuiApplication, QFontMetrics, QColor, QPalette, QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, \
    QPushButton, QLineEdit, QHBoxLayout, QWidget, QHeaderView, QPlainTextEdit, QFileDialog, \
    QDialog, QStackedWidget, QListView, QAction, QMenu, QComboBox, QFileIconProvider
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal, pyqtBoundSignal, QFileInfo
from proc_parse import CollectProcess
import global_seting
import subprocess
import pathlib


class MyTreeWidgetItem(QTreeWidgetItem):
    datum: str

    def __init__(self, *args, **kwargs):
        super(MyTreeWidgetItem, self).__init__(*args, **kwargs)
        self.datum = ""

    def add_data(self, data):
        self.datum = data


class MyTreeWidget(QTreeWidget):
    iconProvider: QFileIconProvider

    kill_process_signal: pyqtBoundSignal
    kill_process_signal = pyqtSignal(list)
    kill_handle_signal: pyqtBoundSignal
    kill_handle_signal = pyqtSignal(list)

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

        self.icon_provider = QFileIconProvider()

    def clear_me(self):
        self.clear()
        self.process_tree = {}  # pid:top_tree_itm
        self.top_items = []

    def build_process_tree(self, list_: list):
        # list_[0] process_name list_[1] pid list_[2] open file path
        if list_[1] in self.process_tree:
            # create follow child file path item
            path_item = MyTreeWidgetItem(self.process_tree[list_[1]])
            path = pathlib.PurePath(list_[2])
            path_item.setText(0, path.name)
            path_item.setText(1, list_[2])
            path_item.setFlags(path_item.flags() | Qt.ItemIsUserCheckable)
            path_item.setCheckState(0, Qt.Unchecked)
            path_item.setIcon(0, self.icon_provider.icon(QFileInfo(list_[2])))  # set icon base on the file extension
        else:
            # create process_name(PID) top item
            tree_item = MyTreeWidgetItem(self)
            tree_item.setText(0, list_[0] + "(" + list_[1] + ")")
            tree_item.setText(1, list_[3])
            tree_item.add_data(list_[1])
            tree_item.setFlags(tree_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)
            tree_item.setIcon(0, self.icon_provider.icon(QFileInfo(list_[3])))

            # create first blank child file path item
            path_item = MyTreeWidgetItem(tree_item)
            path_item.setText(0, "")
            path_item.setHidden(True)
            path_item.setFlags(path_item.flags() | Qt.ItemIsUserCheckable)
            path_item.setCheckState(0, Qt.Unchecked)

            if list_[2] != "":
                path_item = MyTreeWidgetItem(tree_item)
                path = pathlib.PurePath(list_[2])
                path_item.setText(0, path.name)
                path_item.setText(1, list_[2])
                path_item.setIcon(0, self.icon_provider.icon(QFileInfo(list_[2])))
                path_item.setFlags(path_item.flags() | Qt.ItemIsUserCheckable)
                path_item.setCheckState(0, Qt.Unchecked)

            self.process_tree[list_[1]] = tree_item
            self.top_items.append(tree_item)

    def send_to_kill(self):
        kill_process_list = []
        kill_handle_list = []
        for i in range(self.topLevelItemCount()):
            top_itm = self.topLevelItem(i)
            selection_status = int(top_itm.checkState(0))
            if selection_status == 2:  # full selection
                kill_process_list.append(top_itm)
            elif selection_status == 1:  # partial selection
                for j in range(top_itm.childCount()):
                    # top_itm.child(j).text(1) file path
                    if top_itm.child(j).checkState(0) == 2:
                        kill_handle_list.append([top_itm.datum, top_itm.child(j)])
        if kill_process_list:
            self.kill_process_signal.emit(kill_process_list)
        if kill_handle_list:
            self.kill_handle_signal.emit(kill_handle_list)

    def remove_item(self, item: MyTreeWidgetItem):
        parent = item.parent()
        if parent:
            parent.removeChild(item)
            if parent.childCount() == 1:
                self.remove_item(parent)
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
            file_path = self.currentItem().text(1)
        subprocess.run(f'explorer /select,"{file_path}"')


class MyLineEdit(QLineEdit):
    textChanged: pyqtBoundSignal

    def __init__(self, *args, **kwargs):
        super(MyLineEdit, self).__init__(*args, **kwargs)
        self.textChanged.connect(self.on_text_changed)

    def on_text_changed(self):
        self.setText(self.text().replace("/", "\\"))


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
    search_status: QComboBox
    case_sensitive_button: QPushButton

    start_proc_signal: pyqtBoundSignal
    start_proc_signal = pyqtSignal(list)

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
        self.search_status = self.findChild(QComboBox, "search_status")
        self.case_sensitive_button = self.findChild(QPushButton, "case_sensitive_button")

        # replace template widgets to my customized tree widgets
        self.process_tree = MyTreeWidget()
        self.verticalLayout_2.replaceWidget(self.temp_tree, self.process_tree)
        self.file_path_input = MyLineEdit(self.central_widget)
        self.horizontalLayout_2.replaceWidget(self.tmp_file_path_input, self.file_path_input)

        self.file_dialog = MyQFileDialog(self, "Select file to search handles", "", "")

        # delete the old tree widgets
        self.verticalLayout_2.removeWidget(self.temp_tree)
        self.temp_tree.deleteLater()
        self.horizontalLayout_2.removeWidget(self.tmp_file_path_input)
        self.tmp_file_path_input.deleteLater()

        # widget initialize
        self.process_tree.setObjectName("process_tree")
        self.process_tree.setColumnCount(2)
        self.process_tree.setHeaderLabels(["Process name(PID)", "Executable path"])

        self.file_path_input.setText("")
        self.file_path_input.setObjectName("file_path_input")
        self.file_path_input.setPlaceholderText(QCoreApplication.translate("MainWindow", "Drop or input file name"))

        LineEditDragFileInjector(self.file_path_input)
        self.set_status_edit_height(1)
        self.search_status_combo_box_init()

        # connect signals and slots
        self.kill_button.clicked.connect(self.process_tree.send_to_kill)
        self.process_tree.kill_process_signal.connect(self.kill_task.kill_process)
        self.process_tree.kill_handle_signal.connect(self.kill_task.kill_handle)

        self.refresh_pushbutton.clicked.connect(self.send_to_start_proc)
        self.refresh_pushbutton.clicked.connect(self.process_tree.clear_me)
        self.file_path_input.returnPressed.connect(self.send_to_start_proc)
        self.file_path_input.returnPressed.connect(self.process_tree.clear_me)
        self.start_proc_signal.connect(self.start_collect_process)

        self.kill_task.send_kill_status_message.connect(self.append_status_message)
        self.kill_task.clean_killed_tree_item.connect(self.process_tree.remove_item)

        self.file_dialog_button.clicked.connect(self.file_dialog_button_on_clicked)

        self.case_sensitive_button.clicked.connect(self.case_sensitive_toggle)

        # show app
        self.show()

    def auto_adj_size(self):
        q_rect = QGuiApplication.primaryScreen().geometry()
        self.resize(q_rect.width() / 3, q_rect.height() / 3)

    def start_collect_process(self, arg_list: list):
        if self.collect_proc:
            self.collect_proc.kill_exist_process()
        self.collect_proc = CollectProcess(arg_list)  # initialize the process collector
        self.collect_proc.update_tree_signal.connect(self.process_tree.build_process_tree)
        self.collect_proc.complete_signal.connect(self.append_status_message)
        self.collect_proc.start_process()
        self.append_status_message("Searching...")

    def append_status_message(self, message: str):
        self.status_edit.appendPlainText(message)
        max_pos = self.status_edit.verticalScrollBar().maximum()
        self.status_edit.verticalScrollBar().setValue(max_pos)

    def set_status_edit_height(self, n_rows: int):
        p_doc = self.status_edit.document()
        font_metrics = QFontMetrics(p_doc.defaultFont())
        margins = self.status_edit.contentsMargins()
        n_height = (font_metrics.lineSpacing() * n_rows
                    + (p_doc.documentMargin() + self.status_edit.frameWidth()) * 2
                    + margins.top() + margins.bottom())
        self.status_edit.setFixedHeight(n_height+30)
        palette = self.status_edit.palette()
        palette.setColor(QPalette.Base, QColor(240, 240, 240, 255))
        self.status_edit.setPalette(palette)

    def file_dialog_button_on_clicked(self):
        self.file_path_input.setText(self.file_dialog.get_selected_files()[0])

    def search_status_combo_box_init(self):
        self.search_status.addItem("Starts with", "-startswith")
        self.search_status.addItem("Contain", "-contain")

    def send_to_start_proc(self):
        if self.case_sensitive_button.text() == "a":
            self.start_proc_signal.emit([str(self.search_status.currentData()),
                                         str(self.file_path_input.text())])
        else:
            self.start_proc_signal.emit([str(self.search_status.currentData()),
                                         "-case",
                                         str(self.file_path_input.text())])

    def closeEvent(self, a0: QCloseEvent) -> None:
        if self.collect_proc:
            self.collect_proc.kill_exist_process()
        self.kill_task.stop_self_process()

    def case_sensitive_toggle(self):
        # if button is checked
        if self.case_sensitive_button.isChecked():
            # setting text to "A"
            self.case_sensitive_button.setText(QCoreApplication.translate("MainWindow", "A"))
        # if it is unchecked
        else:
            # set background color back to light-grey
            self.case_sensitive_button.setText(QCoreApplication.translate("MainWindow", "a"))
