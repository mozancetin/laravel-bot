from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt
import os
import sys
import utils
import stylesheets
from main import MainWindow

class Start(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()
        self.main()

    def main(self):
        self.pathbox = QtWidgets.QLineEdit("")
        self.pathbox.textChanged.connect(self.on_text_changed)
        self.selectButton = QtWidgets.QPushButton("Select")
        self.selectButton.clicked.connect(self.select)
        self.closeButton = QtWidgets.QPushButton("x")
        self.closeButton.setObjectName("close")
        self.closeButton.clicked.connect(lambda: self.close())
        self.label = QtWidgets.QLabel("Select a path...")
        self.okayButton = QtWidgets.QPushButton("Okay")
        self.okayButton.setDisabled(True)
        self.okayButton.clicked.connect(self.start)

        # if there is an app history
        self.historyLabel = QtWidgets.QLabel("Project History")
        self.historyList = QtWidgets.QListWidget()
        self.historyList.setSelectionMode(QtWidgets.QListWidget.SingleSelection)  # Allow multiple selection
        self.historyList.setFixedHeight(300)
        self.historyList.itemDoubleClicked.connect(self.on_item_double_clicked)
        self.historyList.itemClicked.connect(self.on_item_clicked)

        # Populate the list with items
        items = []
        utils.check_history()
        if os.path.exists("./history.txt"):
            with open("./history.txt", "r", encoding="utf-8") as f:
                for line in f.readlines():
                    items.append(line.strip())
        self.historyList.addItems(items)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.label)
        self.hbox.addStretch()
        self.hbox.addWidget(self.closeButton)

        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.addWidget(self.pathbox)
        self.hbox2.addWidget(self.selectButton)

        self.hbox3 = QtWidgets.QHBoxLayout()
        self.hbox3.addStretch()
        self.hbox3.addWidget(self.okayButton)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox2)
        self.vbox.addWidget(self.historyLabel)
        self.vbox.addWidget(self.historyList)
        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox3)

        self.setLayout(self.vbox)
        self.setWindowTitle("Select a path...")
        self.setFixedHeight(450)
        self.setFixedWidth(600)
        self.setStyleSheet(stylesheets.ssDark)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.center()

    def center(self):
        qr = self.frameGeometry()
        cp = QtWidgets.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.childAt(event.pos()) is None:
            self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        if hasattr(self, 'oldPos'):
            delta = QtCore.QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'oldPos'):
            delattr(self, 'oldPos')

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Return or event.key() == QtCore.Qt.Key_Enter:
            self.okayButton.click()
        else:
            super().keyPressEvent(event)

    def on_item_double_clicked(self, item):
        self.path = item.text()
        self.start()

    def on_item_clicked(self, item):
        self.path = item.text()
        self.pathbox.setText(self.path)
        self.okayButton.setDisabled(False)

    def on_text_changed(self, text):
        if text.strip() == "":
            self.okayButton.setEnabled(False)
            self.path = None
        else:
            path = text.strip()
            file_info = QtCore.QFileInfo(path)
            if file_info.exists() and file_info.isDir():
                self.path = path
                self.okayButton.setEnabled(True)
            else:
                self.okayButton.setEnabled(False)
                self.path = None

    def select(self):
        self.path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select A Save Directory", os.getenv("HOMEPATH") + "\\Desktop")
        if self.path.strip() == "":
            return False
        
        self.okayButton.setDisabled(False)
        self.pathbox.setText(self.path)
        self.start()

    def start(self):
        # Boot the main program        
        self.mw = MainWindow(path = self.path)
        self.close()
        self.mw.show()


app = QtWidgets.QApplication(sys.argv)
window = Start()
window.show()
sys.exit(app.exec_())