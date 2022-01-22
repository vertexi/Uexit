from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QPushButton, QLineEdit
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    process_tree: QTreeWidget
    verticalLayout_2: QVBoxLayout
    kill_button: QPushButton

    def __init__(self):
        super(MainWindow, self).__init__()

        # load ui file
        uic.loadUi("main.ui", self)

        # get widgets
        self.temp_tree = self.findChild(QTreeWidget, "process_tree")
        self.verticalLayout_2 = self.findChild(QVBoxLayout, "verticalLayout_2")
        self.kill_button = self.findChild(QPushButton, "kill_pushbutton")
        self.file_path_input = self.findChild(QLineEdit, "file_path_input")

        # replace template widgets to my customized tree widgets
        self.process_tree = MyTreeWidget()
        self.verticalLayout_2.replaceWidget(self.temp_tree, self.process_tree)

        # delete the old tree widgets
        self.verticalLayout_2.removeWidget(self.temp_tree)
        self.temp_tree.deleteLater()

        self.process_tree.setObjectName("process_tree")
        self.process_tree.setColumnCount(1)
        self.process_tree.setHeaderLabel("Process_name(PID)")

        LineEditDragFileInjector(self.file_path_input)

        # show app
        self.show()


class MyTreeWidget(QTreeWidget):
    def __init__(self, *args, **kwargs):
        super(MyTreeWidget, self).__init__(*args, **kwargs)
        self.process_tree = {}  # pid:tree_itm

    def build_process_tree(self, list_: list):
        # list_[0] process_name list_[1] pid list_[2] open file path
        if list_[1] in self.process_tree:
            # create follow child file path item
            path_item = MyTreeWidgetItem(self.process_tree[list_[1]])
            path_item.setText(0, list_[2])
            path_item.setFlags(path_item.flags() | Qt.ItemIsUserCheckable)
            path_item.setCheckState(0, Qt.Unchecked)
        else:
            # create process_name(PID) top item
            tree_item = MyTreeWidgetItem(self)
            tree_item.setText(0, list_[0] + "(" + list_[1] + ")")
            tree_item.add_data(list_[1])
            tree_item.setFlags(tree_item.flags() | Qt.ItemIsTristate | Qt.ItemIsUserCheckable)

            # create first child file path item
            path_item = MyTreeWidgetItem(tree_item)
            path_item.setText(0, list_[2])
            path_item.setFlags(path_item.flags() | Qt.ItemIsUserCheckable)
            path_item.setCheckState(0, Qt.Unchecked)

            self.process_tree[list_[1]] = tree_item

    def send_to_kill(self):
        for i in range(self.topLevelItemCount()):
            print(self.topLevelItem(i).text(0) + "   ", end='')
            print(self.topLevelItem(i).checkState(0))


class MyTreeWidgetItem(QTreeWidgetItem):
    def __init__(self, *args, **kwargs):
        super(MyTreeWidgetItem, self).__init__(*args, **kwargs)
        self.data = None

    def add_data(self, data):
        self.data = data

    def get_data(self):
        print(self.data)


class LineEditDragFileInjector:
    def __init__(self, line_edit, auto_inject=True):
        self.line_edit = line_edit
        if auto_inject:
            self.inject_dragFile()

    def inject_dragFile(self):
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
