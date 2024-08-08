from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, QComboBox, QCheckBox)
from utils import slug

class ModelWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create the widgets
        self.line_edit = QLineEdit(self)
        self.line_edit2 = QLineEdit(self)
        self.line_edit.setPlaceholderText("Field Slug...")
        self.line_edit2.setPlaceholderText("Field Name...")
        self.combo_box = QComboBox(self)
        self.check_box1 = QCheckBox("Unsigned", self)
        self.check_box2 = QCheckBox("Nullable", self)
        self.check_box3 = QCheckBox("Default", self)
        self.check_box4 = QCheckBox("Slug", self)
        self.check_box5 = QCheckBox("Show In Panel", self)
        
        self.combo_box.addItem("Select Type...")
        # Add options to the combo box
        self.combo_box.addItems(["string", "text", "integer", "boolean"])

        self.combo_box.currentTextChanged.connect(lambda: self.check_box3.setDisabled(self.combo_box.currentText() != "boolean"))
        self.combo_box.currentTextChanged.connect(lambda: self.check_box1.setDisabled(self.combo_box.currentText() != "integer"))
        self.combo_box.currentTextChanged.connect(lambda: self.check_box2.setDisabled(self.combo_box.currentText() == "boolean"))
        self.combo_box.currentTextChanged.connect(lambda: self.check_box4.setDisabled(self.combo_box.currentText() != "string"))
        self.check_box1.setDisabled(True)
        self.check_box2.setDisabled(True)
        self.check_box3.setDisabled(True)
        self.check_box4.setDisabled(True)
        
        # Layout for the checkboxes
        checkboxes_layout = QHBoxLayout()
        checkboxes_layout.addStretch()
        checkboxes_layout.addWidget(self.check_box1)
        checkboxes_layout.addStretch()
        checkboxes_layout.addWidget(self.check_box2)
        checkboxes_layout.addStretch()
        checkboxes_layout.addWidget(self.check_box3)
        checkboxes_layout.addStretch()
        checkboxes_layout.addWidget(self.check_box4)
        checkboxes_layout.addStretch()
        checkboxes_layout.addWidget(self.check_box5)
        checkboxes_layout.addStretch()
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.addWidget(self.line_edit2)
        main_layout.addWidget(self.line_edit)
        main_layout.addWidget(self.combo_box)
        main_layout.addLayout(checkboxes_layout)
        
        self.setLayout(main_layout)

    # def getName(self):
    #     return self.line_edit.text()
    
    # def getType(self):
    #     if self.combo_box.currentText().strip() not in ["Select Type...", ""]:
    #         return self.combo_box.currentText().strip()
    #     else:
    #         return None
        
    # def getCheckboxes(self):
    #     return [self.check_box1.isChecked(), self.check_box2.isChecked(), self.check_box3.isChecked()]
    
    def getValues(self):
        if self.combo_box.currentText().strip() not in ["Select Type...", ""]:
            combo_box_text = self.combo_box.currentText().strip()
        else:
            combo_box_text = None

        return {
            "field_slug" : self.line_edit.text().strip(),
            "field_name" : self.line_edit2.text().strip(),
            "type" : combo_box_text,
            "unsigned" : self.check_box1.isChecked(),
            "nullable" : self.check_box2.isChecked(),
            "default" : self.check_box3.isChecked(),
            "slug" : self.check_box4.isChecked(),
            "show" : self.check_box5.isChecked(),
        }
    
    def setValues(self, values : dict):
        self.line_edit.setText(values.get("field_slug") or slug(values["field_name"]))
        self.line_edit2.setText(values["field_name"])
        self.combo_box.setCurrentText(values["type"])
        self.check_box1.setChecked(values["unsigned"])
        self.check_box2.setChecked(values["nullable"])
        self.check_box3.setChecked(values["default"])
        self.check_box4.setChecked(values["slug"])
        self.check_box5.setChecked(values["show"])
