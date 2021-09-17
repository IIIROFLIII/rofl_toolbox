import os

from PySide2 import QtWidgets, QtGui, QtCore

from rofl_toolbox.generic_python.pyside2_generic import Pyside2Generic
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import ActionButtons

class RemoveScene(QtWidgets.QDialog):
    def __init__(self):
        super(RemoveScene, self).__init__()
        self.setWindowTitle("Remove Scene")
        self.resize(320, 50)
        self.data_and_files = False
        self.datas = False
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
        self.btn_bdd_and_files = ActionButtons("DataBase AND Files")
        self.btn_database = ActionButtons("DataBase")
        self.btn_cancel = ActionButtons("Cancel")

    def modify_widgets(self):
        self.btn_bdd_and_files.setFixedHeight(30)
        self.btn_database.setFixedHeight(30)
        self.btn_cancel.setFixedHeight(30)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.btn_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.btn_layout.addWidget(self.btn_bdd_and_files)
        self.btn_layout.addWidget(self.btn_database)
        self.btn_layout.addWidget(self.btn_cancel)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_bdd_and_files.clicked.connect(self.db_and_files)
        self.btn_database.clicked.connect(self.db)
        self.btn_cancel.clicked.connect(self.close_widget)

    def db_and_files(self):
        self.data_and_files = True
        self.close_widget()

    def db(self):
        self.datas = True
        self.close_widget()

    def close_widget(self):
        self.close()
