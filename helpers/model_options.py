from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal, QPoint, QThread
from customwidgets.ModelWidget import ModelWidget
from workers.createModel import CreateModelWorker
from utils import slug, pascalcase
import stylesheets
import json
import os

class ModelOptions(QtWidgets.QWidget):
    ops = pyqtSignal(dict)
    log = pyqtSignal(str)
    finished = pyqtSignal()

    def __init__(self, path):
        super().__init__()
        self.path = path
        self.options = dict()
        self.main()

    def main(self):
        self.closeButton = QtWidgets.QPushButton("x")
        self.closeButton.setObjectName("close")
        self.closeButton.clicked.connect(self.cancel)
        self.label = QtWidgets.QLabel("Add New Model")

        self.okButton = QtWidgets.QPushButton("Add Model")
        self.cancelButton = QtWidgets.QPushButton("Cancel")
        self.okButton.clicked.connect(self.ok)
        self.cancelButton.clicked.connect(self.cancel)

        self.nameLabel = QtWidgets.QLabel("Model Name:")
        self.nameText = QtWidgets.QLineEdit()

        self.slugLabel = QtWidgets.QLabel("Model Slug:")
        self.slugText = QtWidgets.QLineEdit()
        self.slugText.setDisabled(True)
        self.slugText.setText(slug(self.nameText.text()))

        self.titleLabel = QtWidgets.QLabel("Model Title:")
        self.titleText = QtWidgets.QLineEdit()
        self.titleText.setDisabled(True)
        self.titleText.setText(pascalcase(self.nameText.text()))

        self.singleActiveCheckbox = QtWidgets.QCheckBox("Single Active")
        self.multipleActiveCheckbox = QtWidgets.QCheckBox("Multiple Active")
        self.sortingCheckbox = QtWidgets.QCheckBox("Sorting")
        self.imageCheckbox = QtWidgets.QCheckBox("Image")
        self.imageReqCheckbox = QtWidgets.QCheckBox("Image Required")
        self.multipleImageCheckbox = QtWidgets.QCheckBox("Multiple Image")
        self.controllerCheckbox = QtWidgets.QCheckBox("Controller")
        self.controllerCheckbox.setChecked(True)

        self.singleActiveCheckbox.stateChanged.connect(lambda: self.multipleActiveCheckbox.setDisabled(self.singleActiveCheckbox.isChecked()))
        self.multipleActiveCheckbox.stateChanged.connect(lambda: self.singleActiveCheckbox.setDisabled(self.multipleActiveCheckbox.isChecked()))
        self.imageReqCheckbox.setDisabled(not self.imageCheckbox.isChecked())
        self.imageCheckbox.stateChanged.connect(lambda: (self.imageReqCheckbox.setDisabled(not self.imageCheckbox.isChecked()), self.imageReqCheckbox.setChecked(False)))

        self.checkboxLayout = QtWidgets.QHBoxLayout()
        self.checkboxLayout.addStretch()
        self.checkboxLayout.addWidget(self.singleActiveCheckbox)
        self.checkboxLayout.addStretch()
        self.checkboxLayout.addWidget(self.multipleActiveCheckbox)
        self.checkboxLayout.addStretch()
        self.checkboxLayout.addWidget(self.sortingCheckbox)
        self.checkboxLayout.addStretch()
        self.checkboxLayout.addWidget(self.imageCheckbox)
        self.checkboxLayout.addStretch()
        self.checkboxLayout.addWidget(self.imageReqCheckbox)
        self.checkboxLayout.addStretch()
        self.checkboxLayout.addWidget(self.multipleImageCheckbox)
        self.checkboxLayout.addStretch()
        self.checkboxLayout.addWidget(self.controllerCheckbox)
        self.checkboxLayout.addStretch()

        self.importButton = QtWidgets.QPushButton("Import Model Settings")
        self.exportButton = QtWidgets.QPushButton("Export Model Settings")

        self.importButton.clicked.connect(self.import_settings)
        self.exportButton.clicked.connect(self.export_settings)

        self.impexpLayout = QtWidgets.QHBoxLayout()
        self.impexpLayout.addWidget(self.importButton)
        self.impexpLayout.addWidget(self.exportButton)

        self.scroll_area_label = QtWidgets.QLabel("Fields")

        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)

        self.scroll_area_widget = QtWidgets.QWidget()
        self.scroll_area_layout = QtWidgets.QVBoxLayout()
        self.scroll_area_widget.setLayout(self.scroll_area_layout)
        self.scroll_area.setWidget(self.scroll_area_widget)
        
        # Add button to add new custom widgets
        self.add_button = QtWidgets.QPushButton("Add Field", self)
        self.add_button.clicked.connect(lambda: self.add_object(None))

        self.nameText.textChanged.connect(lambda: (self.slugText.setText(slug(self.nameText.text())), self.titleText.setText(pascalcase(self.nameText.text()))))
        self.scroll_area.setFixedHeight(120)

        self.vbox1 = QtWidgets.QVBoxLayout()
        self.vbox1.addWidget(self.nameLabel)
        self.vbox1.addWidget(self.nameText)
        self.vbox1.addWidget(self.slugLabel)
        self.vbox1.addWidget(self.slugText)
        self.vbox1.addWidget(self.titleLabel)
        self.vbox1.addWidget(self.titleText)

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addLayout(self.vbox1)

        self.hbox2 = QtWidgets.QHBoxLayout()
        self.hbox2.addWidget(self.okButton)
        self.hbox2.addWidget(self.cancelButton)

        self.closeLayout = QtWidgets.QHBoxLayout()
        self.closeLayout.addWidget(self.label)
        self.closeLayout.addStretch()
        self.closeLayout.addWidget(self.closeButton)

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.closeLayout)
        self.vbox.addStretch()
        self.vbox.addLayout(self.hbox)
        self.vbox.addLayout(self.checkboxLayout)
        self.vbox.addStretch()
        self.vbox.addWidget(self.scroll_area_label)
        self.vbox.addWidget(self.scroll_area)
        self.vbox.addWidget(self.add_button)
        self.vbox.addLayout(self.impexpLayout)
        self.vbox.addLayout(self.hbox2)
        
        self.setLayout(self.vbox)
        self.setFixedSize(650, 480)
        self.setWindowTitle("Select Model Options")
        self.setStyleSheet(stylesheets.ssDark)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.center()

    def add_object(self, custom_widget : QtWidgets.QWidget = None):
        if custom_widget == None:
            custom_widget = ModelWidget(self)

        delete_button = QtWidgets.QPushButton("Delete", self)
        delete_button.clicked.connect(lambda: self.remove_object(custom_widget, separator, delete_button))
        
        separator = QtWidgets.QFrame()
        separator.setFrameShape(QtWidgets.QFrame.HLine)
        separator.setFrameShadow(QtWidgets.QFrame.Sunken)

        widget_layout = QtWidgets.QHBoxLayout()
        widget_layout.addWidget(custom_widget)
        widget_layout.addWidget(delete_button)

        self.scroll_area_layout.addLayout(widget_layout)
        self.scroll_area_layout.addWidget(separator)
        self.scroll_area_widget.adjustSize()

    def remove_object(self, custom_widget, separator, delete_button):
        custom_widget.deleteLater()
        separator.deleteLater()
        delete_button.deleteLater()

    def clear_widgets(self):
        while self.scroll_area_layout.count() > 0:
            item = self.scroll_area_layout.takeAt(0)
            if item:
                widget = item.widget()
                if widget:
                    widget.deleteLater()
                else:
                    layout = item.layout()
                    if layout:
                        while layout.count():
                            child = layout.takeAt(0)
                            if child.widget():
                                child.widget().deleteLater()
                            elif child.layout():
                                self.clear_layout(child.layout())

    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
            elif child.layout():
                self.clear_layout(child.layout())

    def reset_options(self):
        self.options["model_name"] = self.nameText.text()
        self.options["model_slug"] = self.slugText.text()
        self.options["model_title"] = self.titleText.text()
        self.options["single_active"] = self.singleActiveCheckbox.isChecked()
        self.options["multiple_active"] = self.multipleActiveCheckbox.isChecked()
        self.options["sorting"] = self.sortingCheckbox.isChecked()
        self.options["image"] = self.imageCheckbox.isChecked()
        self.options["image_required"] = self.imageReqCheckbox.isChecked()
        self.options["multiple_image"] = self.multipleImageCheckbox.isChecked()
        self.options["use_controller"] = self.controllerCheckbox.isChecked()
        self.options["fields"] = list()
        for widget in self.scroll_area_widget.children():
            if isinstance(widget, ModelWidget):
                values = widget.getValues()
                self.options["fields"].append(values)

    def disableButtons(self, c : bool):
        self.okButton.setDisabled(c)
        self.add_button.setDisabled(c)
        self.closeButton.setDisabled(c)
        self.cancelButton.setDisabled(c)
        self.exportButton.setDisabled(c)
        self.importButton.setDisabled(c)

    def ok(self):
        self.reset_options()

        self.log.emit(str(self.options))
        self.ops.emit(self.options)
        self.finished.emit()
        self.close()
        
        # self.th = QThread()
        # self.worker = CreateModelWorker(path=self.path, options=self.options)
        # self.worker.moveToThread(self.th)
        # self.th.started.connect(self.worker.start)
        # self.worker.finished.connect(self.th.quit)
        # self.worker.finished.connect(self.worker.deleteLater)
        # self.th.finished.connect(self.th.deleteLater)

        # self.worker.log.connect(lambda log: self.log.emit(log, end=None))
        # self.worker.success.connect(lambda x: self.log.emit("Success") if x else self.log.emit("No success"))
        # self.worker.finished.connect(lambda: (self.disableButtons(False), self.ops.emit(self.options), self.finished.emit(), self.close()))

        # self.disableButtons(True)
        # self.th.start()        

    def cancel(self):
        self.ops.emit(dict())
        self.finished.emit()
        self.close()

    def export_settings(self):
        export_path = QtWidgets.QFileDialog.getExistingDirectory(self, "Select A Save Directory", os.getcwd() + "\\precreated_models")
        if export_path.strip() == "":
            return False
        
        self.reset_options()

        with open(export_path + f"\\{self.options['model_slug']}_settings.json", "w", encoding="utf-8-sig") as f:
            f.write(json.dumps(self.options, indent=4, ensure_ascii=False))

    def import_settings(self):
        import_path = QtWidgets.QFileDialog.getOpenFileName(self, "Select A File", os.getcwd() + "\\precreated_models", "*.json")[0]
        if import_path.strip() == "":
            return False

        self.clear_widgets()

        with open(import_path, "r", encoding="utf-8-sig") as f:
            settings = json.loads(f.read())

        self.nameText.setText(settings["model_name"])
        # self.slugText.setText(settings["model_slug"])
        # self.titleText.setText(settings["model_title"])
        self.singleActiveCheckbox.setChecked(settings["single_active"])
        self.multipleActiveCheckbox.setChecked(settings["multiple_active"])
        self.sortingCheckbox.setChecked(settings["sorting"])
        self.imageCheckbox.setChecked(settings["image"])
        self.imageReqCheckbox.setChecked(settings["image_required"])
        self.multipleImageCheckbox.setChecked(settings["multiple_image"])
        self.controllerCheckbox.setChecked(settings["use_controller"])

        for field in settings["fields"]:
            model_widget = ModelWidget(self)
            model_widget.setValues(field)
            self.add_object(model_widget)

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
            delta = QPoint(event.globalPos() - self.oldPos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.oldPos = event.globalPos()

    def mouseReleaseEvent(self, event):
        if hasattr(self, 'oldPos'):
            delattr(self, 'oldPos')