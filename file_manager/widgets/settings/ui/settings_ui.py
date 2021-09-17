import os

from PySide2 import QtWidgets, QtCore, QtGui

from rofl_toolbox.file_manager.constants import USER_HOME, MSG
from rofl_toolbox.file_manager.widgets.settings.api.settings import Settings
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import ActionButtons

class SettingsUi(QtWidgets.QWidget):
    def __init__(self):
        super(SettingsUi, self).__init__()

        self.resize(1280, 720)
        self.settings = Settings()
        self.setup_ui()

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_main.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))

        self.create_widgets()
        self.modify_widgets()
        self.create_layout()
        self.add_widgets_to_layout()
        self.setup_connections()

    def create_widgets(self):
        # BTN
        self.btn_database = ActionButtons("...")
        self.btn_files = ActionButtons("...")
        self.btn_revert_data = ActionButtons("")
        self.btn_revert_files = ActionButtons("")
        self.btn_revert_fps = ActionButtons("")

        # GROUPBOX
        self.group_database = QtWidgets.QGroupBox("DataBase")
        self.group_files = QtWidgets.QGroupBox("Files")
        self.group_player = QtWidgets.QGroupBox("Player")

        # LABEL
        self.lbl_database = QtWidgets.QLabel("DataBase Directory   ")
        self.lbl_fps = QtWidgets.QLabel("FPS Default Value       ")
        self.lbl_files = QtWidgets.QLabel("Files Directory           ")

        # LINE EDIT
        self.le_database = QtWidgets.QLineEdit()
        self.le_files = QtWidgets.QLineEdit()

        # SPINBOX
        self.spn_fps = QtWidgets.QSpinBox()

    def modify_widgets(self):
        # BTN
        self.btn_database.setFixedSize(QtCore.QSize(33, 33))
        self.btn_files.setFixedSize(QtCore.QSize(33, 33))

        self.btn_revert_files.setFixedSize(QtCore.QSize(33, 33))
        self.btn_revert_files.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../../../../resources/icons/undo_white.png")))
        self.btn_revert_files.setIconSize(QtCore.QSize(20, 20))

        self.btn_revert_data.setFixedSize(QtCore.QSize(33, 33))
        self.btn_revert_data.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../../../../resources/icons/undo_white.png")))
        self.btn_revert_data.setIconSize(QtCore.QSize(20, 20))

        self.btn_revert_fps.setFixedSize(QtCore.QSize(33, 33))
        self.btn_revert_fps.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../../../../resources/icons/undo_white.png")))
        self.btn_revert_fps.setIconSize(QtCore.QSize(20, 20))

        # GROUPBOX
        self.group_database.setMaximumHeight(100)
        self.group_files.setMaximumHeight(130)

        # LINEEDIT
        self.le_database.setReadOnly(True)
        self.le_database.setText(self.settings.get_bdd_dir())
        self.le_files.setText(self.settings.get_files_folder())
        self.le_files.setReadOnly(True)

        # SPINBOX
        self.spn_fps.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spn_fps.setFixedSize(QtCore.QSize(60, 25))
        self.spn_fps.setAlignment(QtCore.Qt.AlignCenter)
        self.spn_fps.setValue(self.settings.get_fps())
        self.spn_fps.setMaximum(999)

    def create_layout(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.database_layout = QtWidgets.QVBoxLayout()
        self.database_dir_layout = QtWidgets.QHBoxLayout()

        self.files_layout = QtWidgets.QVBoxLayout()
        self.files_dir_layout = QtWidgets.QHBoxLayout()

        self.player_layout = QtWidgets.QVBoxLayout()
        self.fps_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layout(self):
        self.database_dir_layout.addWidget(self.lbl_database)
        self.database_dir_layout.addWidget(self.le_database)
        self.database_dir_layout.addWidget(self.btn_database)
        self.database_dir_layout.addWidget(self.btn_revert_data)
        self.database_dir_layout.addStretch()
        self.database_layout.addLayout(self.database_dir_layout)
        self.database_layout.addStretch()
        self.group_database.setLayout(self.database_layout)

        self.files_dir_layout.addWidget(self.lbl_files)
        self.files_dir_layout.addWidget(self.le_files)
        self.files_dir_layout.addWidget(self.btn_files)
        self.files_dir_layout.addWidget(self.btn_revert_files)
        self.files_dir_layout.addStretch()

        self.files_layout.addLayout(self.files_dir_layout)
        self.files_layout.addStretch()
        self.group_files.setLayout(self.files_layout)

        self.fps_layout.addWidget(self.lbl_fps)
        self.fps_layout.addWidget(self.spn_fps)
        self.fps_layout.addWidget(self.btn_revert_fps)
        self.fps_layout.addStretch()
        self.player_layout.addLayout(self.fps_layout)
        self.player_layout.addStretch()
        self.group_player.setLayout(self.player_layout)

        self.main_layout.addWidget(self.group_database)
        self.main_layout.addWidget(self.group_files)
        self.main_layout.addWidget(self.group_player)
        self.main_layout.addStretch()

    def setup_connections(self):
        # BTN
        self.btn_database.clicked.connect(self.database_path)
        self.btn_files.clicked.connect(self.files_path)
        self.btn_revert_files.clicked.connect(self.revert_files)
        self.btn_revert_data.clicked.connect(self.revert_data)
        self.btn_revert_fps.clicked.connect(self.revert_fps)

        # SPINBOX
        self.spn_fps.valueChanged.connect(self.change_fps)

    def change_fps(self):
        """
        modify fps setting

        """
        self.settings.modify_fps(value=self.spn_fps.value())
        msg = MSG["RESTART"]
        self.nativeParentWidget().statusBar.showMessage(msg, 10000)

    def database_path(self):
        """
        modify database_path setting

        """
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        folder = self.le_files.text()
        file_dialog.setDirectory(folder)
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            folder = file_dialog.selectedFiles()[0]
            self.le_database.setText(folder)
            self.settings.modify_data_path(new_path=folder)
            msg = MSG["RESTART"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)

    def files_path(self):
        """
        modify files_path setting

        """
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setFileMode(QtWidgets.QFileDialog.DirectoryOnly)
        folder = USER_HOME if not self.le_files == self.settings.default_files_folder else self.le_files.text()
        file_dialog.setDirectory(folder)
        if file_dialog.exec_() == QtWidgets.QDialog.Accepted:
            folder = file_dialog.selectedFiles()[0]
            self.le_files.setText(folder)
            self.settings.modify_files_path(new_path=folder)
            msg = MSG["RESTART"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)

    def revert_data(self):
        """
        apply setting default data directory value

        """
        self.le_database.setText(self.settings.default_bdd_dir)
        self.settings.modify_data_path(new_path=self.settings.default_bdd_dir)
        msg = MSG["RESTART"]
        self.nativeParentWidget().statusBar.showMessage(msg, 10000)

    def revert_files(self):
        """
        apply setting default files directory value

        """
        self.le_files.setText(self.settings.default_files_folder)
        self.settings.modify_files_path(new_path=self.settings.default_files_folder)
        msg = MSG["RESTART"]
        self.nativeParentWidget().statusBar.showMessage(msg, 10000)

    def revert_fps(self):
        """
        apply setting default fps value

        """
        self.spn_fps.setValue(self.settings.default_fps)
        self.settings.modify_fps(value=self.settings.default_fps)
        msg = MSG["RESTART"]
        self.nativeParentWidget().statusBar.showMessage(msg, 10000)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    fenetre = SettingsUi()
    fenetre.show()
    app.exec_()