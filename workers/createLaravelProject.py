import os
import json
from PyQt5.QtCore import QObject, pyqtSignal, QProcess

class CreateLaravelProjectWorker(QObject):

    log = pyqtSignal(str)
    finished = pyqtSignal()
    success = pyqtSignal(bool)
    
    def __init__(self, path, name) -> None:
        super().__init__()
        self.path = path
        self.name = name

    def start(self):
        self.log.emit(os.path.join(self.path, self.name))
        self.process = QProcess(self)
        self.process.readyReadStandardOutput.connect(lambda: self.logger("output"))
        self.process.readyReadStandardError.connect(lambda: self.logger("error"))
        self.process.finished.connect(self.process_finished) 

        self.process.start('cmd')
        self.process.waitForStarted()
        self.log.emit("Process has been started...")
        self.process.write((f"cd {self.path}\n").encode())
        self.process.write((f"composer create-project --prefer-dist laravel/laravel {self.name}\n").encode())
        self.process.write((f"cd {os.path.join(self.path, self.name)}\n").encode())

        self.process.write(('exit\n').encode())

    def logger(self, type):
        if type == "output":
            output = self.process.readAllStandardOutput().data().decode('utf-8-sig', 'ignore')
        else:
            output = self.process.readAllStandardError().data().decode('utf-8-sig', 'ignore')
        self.log.emit(output)

    def process_finished(self):
        with open(os.path.join(self.path, self.name) + "/bot_options.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(dict(), indent=4))
            
        self.success.emit(True)
        self.finished.emit()