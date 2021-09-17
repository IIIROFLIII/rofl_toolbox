import os

from PySide2 import QtWidgets, QtGui, QtCore

from rofl_toolbox.generic_python.pyside2_generic import Pyside2Generic
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import ActionButtons
from rofl_toolbox.file_manager.constants import MSG

class AddProject(QtWidgets.QDialog):
    def __init__(self):
        super(AddProject, self).__init__()
        self.alias = None
        self.path = None
        self.setWindowTitle("Add Project")
        self.resize(500, 50)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                    "../../../../resources/icons/rofl_logo.png")))
        self.setup_ui()

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_main.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        Pyside2Generic().center_on_screen(self)

    def create_widgets(self):
        self.lbl_error = QtWidgets.QLabel("")
        self.lbl_alias = QtWidgets.QLabel("Project Alias")
        self.lbl_path = QtWidgets.QLabel("Project Path")
        self.le_alias = QtWidgets.QLineEdit()
        self.le_path = QtWidgets.QLineEdit()
        self.btn_path = QtWidgets.QPushButton()
        self.btn_ok = ActionButtons("OK")
        self.btn_cancel = ActionButtons("Cancel")

    def modify_widgets(self):
        self.btn_path.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                       "../../../../resources/icons/folder.png")))
        self.btn_path.setFixedSize(QtCore.QSize(30, 30))
        self.btn_path.setIconSize(QtCore.QSize(20, 20))
        self.btn_ok.setFixedHeight(30)
        self.btn_cancel.setFixedHeight(30)
        self.lbl_error.setStyleSheet("color: rgb(255, 100, 100)")

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.alias_layout = QtWidgets.QHBoxLayout()
        self.path_layout = QtWidgets.QHBoxLayout()
        self.btn_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.alias_layout.addWidget(self.lbl_alias)
        self.alias_layout.addWidget(self.le_alias)

        self.path_layout.addWidget(self.lbl_path)
        self.path_layout.addWidget(self.le_path)
        self.path_layout.addWidget(self.btn_path)

        self.btn_layout.addWidget(self.lbl_error)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_ok)
        self.btn_layout.addWidget(self.btn_cancel)

        self.main_layout.addLayout(self.alias_layout)
        self.main_layout.addLayout(self.path_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        QtWidgets.QShortcut(QtGui.QKeySequence('Enter'), self, self.validate)
        self.btn_path.clicked.connect(self.open_explorer)
        self.btn_ok.clicked.connect(self.validate)
        self.btn_cancel.clicked.connect(self.close_widget)

    def open_explorer(self):
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        doc_dir = QtCore.QStandardPaths.writableLocation(QtCore.QStandardPaths.DocumentsLocation)
        file_dialog.setDirectory(doc_dir)
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            folder = file_dialog.selectedFiles()[0]
            self.le_path.setText(folder)

    def validate(self):
        if not self.le_alias.text():
            msg = MSG["ENTER_ALIAS"]
            self.lbl_error.setText(msg)
            return False

        if not os.path.exists(self.le_path.text()):
            msg = MSG["ENTER_PROJECT_PATH"]
            self.lbl_error.setText(msg)
            return False

        self.close_widget()
        self.alias = self.le_alias.text()
        self.path = self.le_path.text()

    def close_widget(self):
        self.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    fenetre = AddProject()
    fenetre.show()
    app.exec_()
