ssDark = """
QWidget {
    background-color: #121212;
}

QPushButton {
    padding: 0.3em 1em;
    text-decoration: none;
    color: #67c5ff;
    border-style: solid;
    border-width: 1px;
    border-color: #67c5ff;
    border-radius: 2px;
    background-color: #282828;
    font-size: 12px;
}

QPushButton:hover {
    background: #4682B4;
    color: white;
}

QPushButton:pressed {
    background: #004578;
    color: #DEECF9;
}

QPushButton:disabled {
    color: #808080;
    border-color: #808080;
    background-color: #282828;
}

QPushButton#close {
    text-decoration: none;
    color: #67c5ff;
    line-height: 120px;
    border-radius: 2px;
    border-style: solid;
    border-width: 1px;
    text-align: center;
    vertical-align: middle;
    font-weight: bold;
    font-size: 12px;
}

QPushButton#close:hover {
    background-color: #D22B2B;
    color: black;
    border-color: #D22B2B;
}

QPushButton#close:pressed {
    background-color: #731717;
    color: black;
    border-color: #D22B2B;
}

QPushButton#themeButton {
    width: 25px;
}

QTextEdit {
    background-color: #282828;
    color: #67c5ff;
    font-size: 12px;
}

QScrollBar:vertical {
    width: 0px;
    height: 0px;
}

QLabel {
    color: #67c5ff;
    font-size: 12px;
}

QLabel#title {
    color: #67c5ff;
    font-size: 16px;
    qproperty-alignment: AlignCenter;
    font-weight: bold;
}

QListWidget {
    color: #67c5ff;
    background-color: #282828;
    font-size: 15px;
}

QLineEdit {
    color: #67c5ff;
    background-color: #282828;
    font-size: 15px;
    border-style: solid;
    border-width: 1px;
}

QCheckBox {
    color: #67c5ff;
    font-size: 12px;
    border-style: solid;
}

QCheckBox:disabled {
    color: #808080;
    border-color: #808080;
    font-size: 12px;
}

QComboBox {
    background-color: #282828;
    color: #67c5ff;
    font-size: 15px;
    border-style: solid;
    border-width: 1px;
    height: 22px;
}

QAbstractItemView {
    background-color: #282828;
    color: #67c5ff;
    font-size: 12px;
}

QAbstractItemView::item {
    height: 25px;
}
"""

ssLight = """
QWidget {
    background-color: #71AFE5;
}

QPushButton {
    padding: 0.3em 1em;
    text-decoration: none;
    color: black;
    border-style: solid;
    border-width: 1px;
    border-color: #2B88D8;
    border-radius: 2px;
    background-color: #C7E0F4;
    font-size: 12px;
}

QPushButton:hover {
    background: #4682B4;
    border-color: black;
}

QPushButton:pressed {
    background: #106EBE;
    color: black;
}

QPushButton#close {
    text-decoration: none;
    color: black;
    line-height: 120px;
    border-radius: 2px;
    border-style: solid;
    border-width: 1px;
    text-align: center;
    vertical-align: middle;
    font-weight: bold;
    font-size: 12px;
}

QPushButton#close:hover {
    background-color: #D22B2B;
    color: black;
    border-color: #D22B2B;
}

QPushButton#close:pressed {
    background-color: #731717;
    color: black;
    border-color: #D22B2B;
}

QPushButton#themeButton {
    width: 25px;
}

QTextEdit {
    background-color: #C7E0F4;
    color: black;
    font-size: 12px;
}

QScrollBar:vertical {
    width: 0px;
    height: 0px;
}

QLabel {
    color: black;
    font-size: 12px;
}

QLabel#title {
    color: black;
    font-size: 16px;
    qproperty-alignment: AlignCenter;
    font-weight: bold;
}

QListWidget {
    color: black;
    background-color: #C7E0F4;
    font-size: 15px;
}

QLineEdit {
    color: black;
    background-color: #C7E0F4;
    font-size: 15px;
    border-style: solid;
    border-width: 1px;
}

QComboBox {
    background-color: #C7E0F4;
    color: black;
    font-size: 12px;
    border-style: solid;
    height: 20px;
}

QAbstractItemView {
    background-color: #C7E0F4;
    color: black;
    font-size: 12px;
}

QAbstractItemView::item {
    height: 25px;
}
"""