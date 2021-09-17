import os

from PySide2 import QtWidgets, QtCore, QtGui

from rofl_toolbox.generic_python.pyside2_generic import Pyside2Generic
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import ActionButtons
from rofl_toolbox.file_manager.constants import MSG

class AddScene(QtWidgets.QDialog):
    def __init__(self, name=False, task=False, step=False):
        super(AddScene, self).__init__()
        self._name_info = None
        self._task_info = None
        self._step_info = None
        self.name = name
        self.task = task
        self.step = step
        self.setWindowTitle("Add Scene")
        self.resize(320, 50)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                    "../../../../resources/icons/rofl_logo.png")))
        self.setup_ui()

    @property
    def name_info(self):
        if self.name:
            return self._name_info

    @property
    def task_info(self):
        if self.task:
            return self._task_info

    @property
    def step_info(self):
        if self.step:
            return self._step_info

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

    def _add_name_package(self):
        if not self.name:
            return False

        self.lbl_name = QtWidgets.QLabel("Name: ")
        self.le_name = QtWidgets.QLineEdit()
        self.le_name.setFixedSize(QtCore.QSize(220, 35))
        self.le_name.setText("test")

        self.name_layout = QtWidgets.QHBoxLayout()
        self.name_layout.addWidget(self.lbl_name)
        self.name_layout.addStretch()
        self.name_layout.addWidget(self.le_name)

        self.main_layout.addLayout(self.name_layout)

    def _add_task_package(self):
        if not self.task:
            return False

        self.lbl_task = QtWidgets.QLabel("Task: ")
        self.le_task = QtWidgets.QLineEdit()
        self.le_task.setFixedSize(QtCore.QSize(220, 35))
        self.le_task.setText("fx3d")

        self.task_layout = QtWidgets.QHBoxLayout()
        self.task_layout.addWidget(self.lbl_task)
        self.task_layout.addStretch()
        self.task_layout.addWidget(self.le_task)

        self.main_layout.addLayout(self.task_layout)

    def _add_step_package(self):
        if not self.step:
            return False

        self.lbl_step = QtWidgets.QLabel("Step: ")
        self.le_step = QtWidgets.QLineEdit()
        self.le_step.setFixedSize(QtCore.QSize(220, 35))
        self.le_step.setText("main")

        self.step_layout = QtWidgets.QHBoxLayout()
        self.step_layout.addWidget(self.lbl_step)
        self.step_layout.addStretch()
        self.step_layout.addWidget(self.le_step)

        self.main_layout.addLayout(self.step_layout)

    def _validate_name(self):
        if not self.name:
            return False
        if not self.le_name.text():
            msg = MSG["ENTER_NAME"]
            self.lbl_error.setText(msg)
            return False

        self._name_info = self.le_name.text().replace(" ", "_")

    def _validate_task(self):
        if not self.task:
            return False
        if not self.le_task.text():
            msg = MSG["ENTER_TASK"]
            self.lbl_error.setText(msg)
            return False

        self._task_info = self.le_task.text().replace(" ", "_")

    def _validate_step(self):
        if not self.step:
            return False
        if not self.le_step.text():
            msg = MSG["ENTER_STEP"]
            self.lbl_error.setText(msg)
            return False

        self._step_info = self.le_step.text().replace(" ", "_")

    def create_widgets(self):
        self.lbl_error = QtWidgets.QLabel("")
        self.btn_ok = ActionButtons("OK")
        self.btn_cancel = ActionButtons("Cancel")

    def modify_widgets(self):
        self.btn_ok.setFixedHeight(30)
        self.btn_cancel.setFixedHeight(30)
        self.lbl_error.setStyleSheet("color: rgb(255, 100, 100)")

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.btn_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self):
        self._add_name_package()
        self._add_task_package()
        self._add_step_package()

        self.btn_layout.addWidget(self.lbl_error)
        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.btn_ok)
        self.btn_layout.addWidget(self.btn_cancel)

        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.btn_ok.clicked.connect(self.validate)
        self.btn_cancel.clicked.connect(self.close_widget)

    def validate(self):
        self._validate_name()
        self._validate_task()
        self._validate_step()
        self.close_widget()

    def close_widget(self):
        self.close()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    fenetre = AddScene(name=True, task=True, step=True)
    fenetre.show()
    app.exec_()
