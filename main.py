from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui
from PyQt5.QtCore import Qt, QThread
from workers.createLaravelProject import CreateLaravelProjectWorker
from workers.createAdminPanel import CreateAdminPanelWorker
from workers.resetRouting import ResetRoutingWorker
from workers.createModel import CreateModelWorker
from helpers.model_options import ModelOptions
import os
import utils
import stylesheets
import paths

class MainWindow(QtWidgets.QWidget):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.get_options()
        self.main()

    def get_options(self):
        if os.path.exists(os.path.join(self.path, "bot_options.json")):
            self.options_exists = True
            self.options = utils.get_bot_options(self.path)
        else:
            self.options_exists = False
            self.options = dict()

    def main(self):
        self.closeButton = QtWidgets.QPushButton("x")
        self.closeButton.setObjectName("close")
        self.closeButton.clicked.connect(lambda: self.close())
        self.label = QtWidgets.QLabel("Bot Main - " + self.path)
        self.logger = QtWidgets.QTextEdit()
        self.logger.setReadOnly(True)
        self.logger.setFixedSize(400, 250)
        self.models = QtWidgets.QListWidget()
        self.models.setFixedSize(400, 250)
        self.models.setSelectionMode(QtWidgets.QListWidget.SingleSelection)
        if self.options_exists:
            self.changingLabel = QtWidgets.QLabel("Models")
            self.setModels()
            self.addModelButton = QtWidgets.QPushButton("Add New Model")
            self.addModelButton.setFixedWidth(400)
            self.addModelButton.clicked.connect(self.addModel)

            self.htmlToBladeButton = QtWidgets.QPushButton("Convert All HTML to Blade")
            self.htmlToBladeButton.setFixedWidth(400)
            self.htmlToBladeButton.clicked.connect(self.htmlToBlade)

            self.buildButton = QtWidgets.QPushButton("Build Models")
            self.buildButton.setFixedWidth(400)
            self.buildButton.clicked.connect(self.build)
            
            self.changeBox = QtWidgets.QPushButton("Logs")
            self.changeBox.setFixedWidth(400)
            self.changeBox.clicked.connect(lambda: self.hideLogger(self.changingLabel.text() == "Logs"))

            self.checkForBuild()
            check = utils.check_for_html(self.path + paths.VIEWS)
            if not check and check != None:
                self.htmlToBladeButton.setDisabled(True)

            self.programVBox = QtWidgets.QVBoxLayout()
            self.programVBox.addStretch()
            self.programVBox.addWidget(self.htmlToBladeButton)
            self.programVBox.addWidget(self.addModelButton)
            self.programVBox.addWidget(self.buildButton)
            self.programVBox.addWidget(self.changeBox)
            self.programVBox.addSpacing(20)
            self.programVBox.addWidget(self.changingLabel)
            self.programVBox.addWidget(self.logger)
            self.programVBox.addWidget(self.models)
            self.programVBox.addStretch()
            
        else:
            self.changingLabel = QtWidgets.QLabel("Logs")
            self.projectNameLabel = QtWidgets.QLabel("Project Name:")
            self.projectNameInput = QtWidgets.QLineEdit()
            self.projectNameInput.setFixedWidth(400)
            self.imageOnAdminCheckbox = QtWidgets.QCheckBox("Image (Admin)")
            self.createProjectButton = QtWidgets.QPushButton("Create New Laravel Project")
            self.createProjectButton.setFixedWidth(400)
            self.createProjectButton.clicked.connect(self.createLaravelProject)

            self.createProjectVBox = QtWidgets.QVBoxLayout()
            self.createProjectVBox.addStretch()
            self.createProjectVBox.addWidget(self.projectNameLabel)
            self.createProjectVBox.addWidget(self.projectNameInput)
            self.createProjectVBox.addWidget(self.imageOnAdminCheckbox)
            self.createProjectVBox.addWidget(self.createProjectButton)
            self.createProjectVBox.addSpacing(40)
            self.createProjectVBox.addWidget(self.changingLabel)
            self.createProjectVBox.addWidget(self.logger)
            self.createProjectVBox.addStretch()

        self.hbox = QtWidgets.QHBoxLayout()
        self.hbox.addWidget(self.label)
        self.hbox.addStretch()
        self.hbox.addWidget(self.closeButton)

        self.hbox2 = QtWidgets.QHBoxLayout()
        if not self.options_exists:
            self.hbox2.addStretch()
            self.hbox2.addLayout(self.createProjectVBox)
            self.hbox2.addStretch()
        else:
            self.hbox2.addStretch()
            self.hbox2.addLayout(self.programVBox)
            self.hbox2.addStretch()

        self.vbox = QtWidgets.QVBoxLayout()
        self.vbox.addLayout(self.hbox)
        # self.vbox.addStretch()
        self.vbox.addLayout(self.hbox2)
        #self.vbox.addStretch()

        self.setLayout(self.vbox)
        self.setWindowTitle("Bot Main - " + self.path)
        self.setFixedWidth(450)
        self.setFixedHeight(500)
        self.setStyleSheet(stylesheets.ssDark)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.center()

    def setModels(self):
        if self.options.get("models") != None and self.options["models"] != {"Admin": {}}:
            self.models.clear()
            for model in self.options["models"].keys():
                if model != "Admin":
                    self.models.addItem(model if model not in self.options["built"] else model + " (BUILT)")

        self.hideLogger(True)

    def setLogBox(self, newText : str):
        text = self.logger.toPlainText()
        if text != "":
            text += "\n"
        text += newText
        self.logger.setText(text)
        self.logger.moveCursor(QtGui.QTextCursor.End)

    def hideLogger(self, c : bool = True):
        if c:
            # self.setFixedHeight(180)
            if self.options_exists and hasattr(self, "changeBox"):
                self.changeBox.setText("Logs")
            self.changingLabel.setText("Models")
            self.logger.setHidden(c)
            self.models.setHidden(not c)
        else:
            # self.setFixedHeight(480)
            if self.options_exists and hasattr(self, "changeBox"):
                self.changeBox.setText("Models")
            self.changingLabel.setText("Logs")
            self.logger.setHidden(c)
            self.models.setHidden(not c)

        self.center()

    def checkForBuild(self):
        if self.options.get("models") == None or len(self.options["models"].keys()) <= 1 or self.options.get("built") == None or self.options["built"] == list(self.options["models"].keys()):
            self.buildButton.setDisabled(True)
        else:
            self.buildButton.setDisabled(False)

    def disableButtons(self, c : bool, mode : bool = False):
        if mode:
            self.addModelButton.setDisabled(c)
            self.buildButton.setDisabled(c)
            check = utils.check_for_html(self.path + paths.VIEWS)
            if check:
                self.htmlToBladeButton.setDisabled(c)
        else:
            self.createProjectButton.setDisabled(c)
        self.closeButton.setDisabled(c)

    def updateRoute(self, path, reload : bool = False):
        self.hideLogger(False)
        def rel():
            self.setLogBox("Routes has been updated")
            if reload:
                self.reload()

        self.th = QThread()
        self.worker = ResetRoutingWorker(path=path, options=self.options)
        self.worker.moveToThread(self.th)
        self.th.started.connect(self.worker.update_routes)
        self.worker.finished.connect(self.th.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.th.finished.connect(self.th.deleteLater)

        self.worker.log.connect(lambda log: self.setLogBox(log))
        self.worker.success.connect(lambda x: self.setLogBox("Success") if x else self.setLogBox("No success"))
        self.worker.finished.connect(rel)

        self.setLogBox("Updating routing...")
        self.th.start()

    def htmlToBlade(self):
        self.hideLogger(False)
        self.setLogBox("Converting HTML files to blade files...")
        utils.html_to_blade_dir(self.path + paths.VIEWS)
        self.setLogBox("All HTML files are converted to blade files")
        self.htmlToBladeButton.setDisabled(True)

    def modelWorkerIterator(self, models : list):
        if len(models) <= 0:
            self.disableButtons(False, True)
            return
        
        def finished():
            if len(models) > 1:
                self.modelWorkerIterator(models[1:])
            else:
                self.updateRoute(self.path)
                self.disableButtons(False, True)
                self.checkForBuild()
                self.setLogBox("All models are generated...")
                self.setModels()

        if models[0] == "Admin":
            self.modelWorkerIterator(models[1:])
        else:
            self.th = QThread(parent=self)
            self.worker = CreateModelWorker(path=self.path, options=self.options["models"][models[0]])
            self.worker.moveToThread(self.th)
            self.th.started.connect(self.worker.start)
            self.worker.finished.connect(self.th.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.th.finished.connect(self.th.deleteLater)

            self.worker.log.connect(lambda log: self.setLogBox(log))
            self.worker.success.connect(lambda x: self.setLogBox("Success") if x else self.setLogBox("No success"))
            self.worker.finished.connect(lambda: finished())

            self.setLogBox("Model is generating: " + models[0])
            self.th.start() 
            # Additional debug self.setLogBox statements
            # self.setLogBox("Thread started:", self.th.isRunning())

    def build(self):
        self.hideLogger(False)
        if self.options.get("models") == None or self.options["models"] == {"Admin":{}}:
            self.setLogBox("No models to build")
            return False
        
        self.disableButtons(True, True)
        if self.options.get("built") == None or len(self.options["built"]) == 0:
            to_build : list = list(self.options["models"].keys())
            self.options["built"] = to_build
        else:
            to_build : list = [modelname for modelname in list(self.options["models"].keys()) if modelname not in self.options["built"]]
            self.options["built"] += to_build

        utils.save_bot_options(self.path, self.options)

        if len(to_build) == 0:
            self.setLogBox("Nothing to build...")
        
        self.modelWorkerIterator(to_build)

    def addModel(self):
        def addOps(ops : dict):
            self.hideLogger(False)
            if ops == dict():
                self.setLogBox("Add Model cancelled")
                self.showNormal()
                return

            self.options["models"][ops["model_title"]] = ops
            utils.save_bot_options(self.path, self.options)
            self.checkForBuild()
            self.setModels()
            self.showNormal()

        if self.options.get("models") == None:
            self.options["models"] = dict()
            self.options["built"] = list()

        self.model_options = ModelOptions(self.path)
        self.hide()
        self.model_options.show()

        self.model_options.ops.connect(lambda ops: addOps(ops))
        self.model_options.log.connect(lambda log: self.setLogBox(log))

    def createAdminPanel(self):
        self.setLogBox("Finished...")
        utils.add_to_history(self.projectDir)

        self.options["models"] = dict()
        self.options["built"] = list()

        def addOps(d):
            self.options["admin_panel"] = True
            self.options["admin_options"] = d
            self.options["models"]["Admin"] = dict()
            ops_finished()
        
        def finished():
            self.setLogBox('Admin panel has been built.')
            utils.save_bot_options(self.projectDir, self.options)
            self.updateRoute(self.projectDir, True)

        def ops_finished():
            if self.options['admin_options'] == dict():
                return False
            
            self.th = QThread()
            self.worker = CreateAdminPanelWorker(path=self.projectDir, options=self.options['admin_options'])
            self.worker.moveToThread(self.th)
            self.th.started.connect(self.worker.start)
            self.worker.finished.connect(self.th.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.th.finished.connect(self.th.deleteLater)

            self.worker.log.connect(lambda log: self.setLogBox(log))
            self.worker.success.connect(lambda x: self.setLogBox("Success") if x else self.setLogBox("No success"))
            self.worker.finished.connect(finished)

            self.setLogBox("Starting to create admin panel: " + self.projectDir)
            self.th.start()

        addOps({"image" : self.imageOnAdminCheckbox.isChecked()})

    def createLaravelProject(self):
        text = self.projectNameInput.text().strip()
        if text != "":
            self.disableButtons(True)
            self.projectDir = os.path.join(self.path, text).replace("\\", "/")
            self.th = QThread()
            self.worker = CreateLaravelProjectWorker(path = self.path, name = text)
            self.worker.moveToThread(self.th)
            self.th.started.connect(self.worker.start)
            self.worker.finished.connect(self.th.quit)
            self.worker.finished.connect(self.worker.deleteLater)
            self.th.finished.connect(self.th.deleteLater)

            self.worker.log.connect(lambda log: self.setLogBox(log))
            self.worker.success.connect(lambda x: self.setLogBox("Success") if x else self.setLogBox("No success"))
            self.worker.finished.connect(self.createAdminPanel)

            self.setLogBox("Starting to create new laravel project: " + self.projectDir)
            self.th.start()

    def reload(self):
        newmw = MainWindow(path=self.projectDir)
        self.close()
        newmw.showNormal()

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