from PyQt5 import uic
from PyQt5.QtWidgets import QMainWindow, QTreeWidget, QTreeWidgetItem


class MainWindow(QMainWindow):
    process_tree : QTreeWidget

    def __init__(self):
        super(MainWindow, self).__init__()

        # load ui file
        uic.loadUi("main.ui", self)

        # get widgets
        assert self.process_tree
        self.process_tree = self.findChild(QTreeWidget, "process_tree")
        self.process_tree.setColumnCount(1)
        self.process_tree.setHeaderLabel("world")
        temp = QTreeWidgetItem(["hello"])
        temp.addChild(QTreeWidgetItem(["world"]))
        self.process_tree.addTopLevelItem(temp)
        self.process_tree.addTopLevelItem(QTreeWidgetItem(["hello"]))
        self.process_tree.addTopLevelItem(QTreeWidgetItem(["hello"]))
        self.process_tree.addTopLevelItem(QTreeWidgetItem(["hello"]))

        # show app
        self.show()
