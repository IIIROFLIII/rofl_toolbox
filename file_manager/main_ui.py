import os
import shutil

from PySide2 import QtWidgets, QtCore, QtGui

from rofl_toolbox.file_manager.constants import MP4_FOLDER

from rofl_toolbox.generic_python.pyside2_generic import Pyside2Generic

from rofl_toolbox.file_manager.widgets.scene_manager.ui.scene_manager import SceneManager
from rofl_toolbox.file_manager.widgets.file_copyer.ui.file_copyer_ui import FileCopyerUi
from rofl_toolbox.file_manager.widgets.extra_files_manager.ui.extra_files_manager import ExtraFilesManagerUi
from rofl_toolbox.file_manager.widgets.sequence_player.ui.sequence_player_ui import SequencePlayerUi
from rofl_toolbox.file_manager.widgets.settings.ui.settings_ui import SettingsUi

class MainUi(QtWidgets.QMainWindow):
    def __init__(self, software=None):
        super(MainUi, self).__init__()
        self.software = software
        self.setWindowTitle("ROFL Tools")
        self.resize(1200, 790)
        # self.setFixedSize(QtCore.QSize(1200, 790))
        # self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/rofl_logo.png")))
        self.setup_ui()

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../resources/css/style_main.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        Pyside2Generic().center_on_screen(self)

    def create_widgets(self):
        self.tab_main = QtWidgets.QTabWidget()
        self.scene_manager = SceneManager(software=self.software)
        self.file_copyer = FileCopyerUi()
        self.extr_files_manager = ExtraFilesManagerUi(software=self.software)
        self.sequence_player = SequencePlayerUi()
        self.settings_manager = SettingsUi()
        self.statusBar = QtWidgets.QStatusBar()

    def modify_widgets(self):
        tab1 = self.tab_main.addTab(self.scene_manager, "")
        tab2 = self.tab_main.addTab(self.file_copyer, "")
        tab3 = self.tab_main.addTab(self.extr_files_manager, "")
        tab4 = self.tab_main.addTab(self.sequence_player, "")
        tab5 = self.tab_main.addTab(self.settings_manager, "")
        self.tab_main.setTabIcon(tab1, QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../resources/icons/home-page.png")))
        self.tab_main.setTabIcon(tab2, QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../resources/icons/copy.png")))
        self.tab_main.setTabIcon(tab3, QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../resources/icons/extra_files.png")))
        self.tab_main.setTabIcon(tab4, QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../resources/icons/video-player.png")))
        self.tab_main.setTabIcon(tab5, QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../resources/icons/settings.png")))
        self.tab_main.setIconSize(QtCore.QSize(20, 20))
        self.tab_main.setTabPosition(QtWidgets.QTabWidget.West)

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self.tab_main)
        self.player_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.setStatusBar(self.statusBar)
        self.setCentralWidget(self.tab_main)

    def setup_connections(self):
        pass

    def closeEvent(self, event):
        self.file_copyer.stop_all_copy()
        if os.path.exists(MP4_FOLDER):
            shutil.rmtree(MP4_FOLDER)

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    fenetre = MainUi(software="Python")
    fenetre.show()
    app.exec_()
