import os
import shutil

from PySide2 import QtWidgets, QtGui, QtCore

from rofl_toolbox.generic_python.python_generic import Generic
from rofl_toolbox.file_manager.widgets.file_copyer.api.file_copyer import FileCopyer
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import ActionButtons, ComboBox, TreeWidget, Label

class Worker(QtCore.QObject):
    file_copied = QtCore.Signal(int, str, bool)
    finished = QtCore.Signal()

    def __init__(self, parent=None, item=None, scene=None):
        super(Worker, self).__init__()
        self.parent = parent
        self.item = item
        self.scene = scene
        self.runs = True

    def copy_files(self):
        SID_FC = FileCopyer()
        files = SID_FC.get_all_group_files(scene=self.scene, category=self.parent.name, group=self.item.name)
        for i, value in enumerate(files):
            if not self.runs:
                continue
            # check if the file is already copied
            if SID_FC.get_file_status(files=files, file=value):
                continue
            # get source and target
            src = SID_FC.get_file_src(files=files, file=value)
            tgt = SID_FC.get_file_tgt(files=files, file=value)
            # create target folder if not exist
            if not os.path.exists(os.path.dirname(tgt)):
                os.makedirs(os.path.dirname(tgt))
            # do the copy and emit signal
            shutil.copy(src, tgt)
            self.file_copied.emit(i+1, value,True)

        self.finished.emit()

class little_widget(QtWidgets.QWidget):
    def __init__(self, name="", scene="", parent=None, tree=None):
        super(little_widget, self).__init__()

        self.tree = tree
        self.parent = parent
        self.scene = scene
        self.name = name
        self.source_folder = self.get_source_path()
        self.target_folder = self.get_target_path()
        self.setup_ui()

    @property
    def nb_files(self):
        if not self.scene:
            return 0

        SID_FC = FileCopyer()
        return SID_FC.get_all_group_files_number(scene=self.scene, category=self.parent.name, group=self.name)

    @property
    def nb_files_copied(self):
        if not self.parent:
            return 0

        if not self.scene:
            return 0

        SID_FC = FileCopyer()
        return SID_FC.get_all_group_files_copied_number(scene=self.scene, category=self.parent.name, group=self.name)

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_file_copyer.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        # BTN
        self.btn_start = ActionButtons("")
        self.btn_stop = ActionButtons("")
        self.btn_source = ActionButtons("")
        self.btn_target = ActionButtons("")
        # LABEL
        self.lbl_name = QtWidgets.QLabel(self.name[-20:])
        self.lbl_nb_file_copied = QtWidgets.QLabel()
        self.lbl_slash = QtWidgets.QLabel("/")
        self.lbl_nb_files = QtWidgets.QLabel()
        # PROGRESS BAR
        self.prg_progress_bar = QtWidgets.QProgressBar()

    def modify_widgets(self):
        # BTN
        self.btn_start.setFixedSize(QtCore.QSize(30, 30))
        self.btn_start.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/play_white.png")))
        self.btn_stop.setFixedSize(QtCore.QSize(30, 30))
        self.btn_stop.setVisible(False)
        self.btn_stop.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                       "../../../../resources/icons/pause_white.png")))
        self.btn_source.setFixedSize(QtCore.QSize(30, 30))
        self.btn_source.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                         "../../../../resources/icons/folder.png")))
        self.btn_target.setFixedSize(QtCore.QSize(30, 30))
        self.btn_target.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                         "../../../../resources/icons/folder3.png")))
        # LABEL
        self.lbl_name.setFixedSize(QtCore.QSize(150, 20))
        self.lbl_nb_files.setText(str(self.nb_files))
        self.lbl_nb_file_copied.setText(str(self.nb_files_copied))
        self.lbl_nb_files.setFixedWidth(40)
        self.lbl_nb_file_copied.setFixedWidth(40)
        self.lbl_nb_files.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl_nb_file_copied.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        # PROGRESS BAR
        self.prg_progress_bar.setFixedHeight(10)
        self.prg_progress_bar.setRange(0, self.nb_files)
        self.prg_progress_bar.setValue(self.nb_files_copied)
        self.prg_progress_bar.setTextVisible(False)

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_name)
        self.main_layout.addWidget(self.prg_progress_bar)
        self.main_layout.addWidget(self.lbl_nb_file_copied)
        self.main_layout.addWidget(self.lbl_slash)
        self.main_layout.addWidget(self.lbl_nb_files)
        self.main_layout.addWidget(self.btn_start)
        self.main_layout.addWidget(self.btn_stop)
        self.main_layout.addWidget(self.btn_source)
        self.main_layout.addWidget(self.btn_target)

    def setup_connections(self):
        self.btn_start.clicked.connect(self.start_copy)
        self.btn_stop.clicked.connect(self.stop_copy)
        self.btn_source.clicked.connect(self.open_source)
        self.btn_target.clicked.connect(self.open_target)

    def file_copied(self, number, name, success):
        """
        what happened when the file is fully copied
        Args:
            number: the number of the file
            name: the name of the file
            success: copy validation

        """
        if not success:
            return False

        self.lbl_nb_file_copied.setText(str(number))
        self.prg_progress_bar.setValue(number)
        SID_FC = FileCopyer()
        SID_FC.set_file_status(scene=self.scene, category=self.parent.name, group=self.name, file=name)

    def finished_copy(self):
        """
        what happened when all the files are copied

        """
        self.thread.quit()
        self.btn_stop.setVisible(False)
        self.btn_start.setVisible(True)

        if not self.nb_files == self.nb_files_copied:
            return False

        self.lbl_nb_file_copied.setText(str(self.nb_files))
        self.btn_start.setDisabled(True)
        root = self.tree.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if not item is self.parent:
                continue
            # remove file in filecopyer database
            SID_FC = FileCopyer()
            SID_FC.remove_in_data_files(scene=self.scene, category=item.widget.name, group=self.name)

            nb_files = int(item.widget.lbl_nb_file_copied.text())
            item.widget.lbl_nb_file_copied.setText(str(nb_files+1))
            item.widget.prg_progress_bar.setValue(nb_files+1)

            if not item.widget.lbl_nb_file_copied.text() == item.widget.lbl_nb_files.text():
                continue

            item.widget.btn_start.setVisible(True)
            item.widget.btn_stop.setVisible(False)
            item.widget.btn_start.setDisabled(True)

    def get_source_path(self):
        """
        get the source folder
        Returns: the source folder

        """
        SID_FC = FileCopyer()
        folder_path = SID_FC.get_source_folder(scene=self.scene, category=self.parent.widget.name, group=self.name)

        return folder_path

    def get_target_path(self):
        """
        get the target folder
        Returns:the target folder

        """
        SID_FC = FileCopyer()
        folder_path = SID_FC.get_target_folder(scene=self.scene, category=self.parent.widget.name, group=self.name)

        return folder_path

    def open_source(self):
        """
        open explorer on source folder

        """
        if not os.path.isdir(self.source_folder):
            return False

        Generic().open_folder(self.source_folder)

    def open_target(self):
        """
        open explorer on target folder

        """
        if not os.path.isdir(self.target_folder):
            return False

        Generic().open_folder(self.target_folder)

    def start_copy(self):
        """
        launch copy in an other thread

        """
        if self.lbl_nb_files.text() == self.lbl_nb_file_copied.text():
            return False

        self.btn_stop.setVisible(True)
        self.btn_start.setVisible(False)
        self.thread = QtCore.QThread(self)
        self.worker = Worker(parent=self.parent, item=self, scene=self.scene)
        self.worker.moveToThread(self.thread)
        self.worker.file_copied.connect(self.file_copied)
        self.thread.started.connect(self.worker.copy_files)
        self.worker.finished.connect(self.finished_copy)
        self.thread.start()

    def stop_copy(self):
        """
        stop copy thread

        """
        # if not self.btn_stop.isVisible():
        #     return False

        # if not self.worker.runs:
        #     return False

        self.worker.runs = False
        self.thread.quit()
        self.btn_start.setVisible(True)
        self.btn_stop.setVisible(False)

class parent_widget(QtWidgets.QWidget):
    def __init__(self, name="", scene="", tree=None):
        super(parent_widget, self).__init__()

        self.tree = tree
        self.scene = scene
        self.name = name
        self.setup_ui()

    @property
    def nb_files(self):
        if not self.scene:
            return 0

        SID_FC = FileCopyer()
        return SID_FC.get_all_scene_categories_groups_number(scene=self.scene, category=self.name)

    @property
    def nb_files_copied(self):
        return 0

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_file_copyer.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        # BTN
        self.btn_start = ActionButtons("")
        self.btn_stop = ActionButtons("")
        # LABELS
        self.lbl_name = QtWidgets.QLabel(self.name)
        self.lbl_nb_file_copied = QtWidgets.QLabel()
        self.lbl_slash = QtWidgets.QLabel("/")
        self.lbl_nb_files = QtWidgets.QLabel()
        # PROGRESS BAR
        self.prg_progress_bar = QtWidgets.QProgressBar()

    def modify_widgets(self):
        # BTN
        self.btn_start.setFixedSize(QtCore.QSize(30, 30))
        self.btn_start.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/play_white.png")))
        self.btn_stop.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                       "../../../../resources/icons/pause_white.png")))
        self.btn_stop.setFixedSize(QtCore.QSize(30, 30))
        self.btn_stop.setVisible(False)
        # LABELS
        self.lbl_name.setFixedSize(QtCore.QSize(150, 20))
        self.lbl_nb_files.setText(str(self.nb_files))
        self.lbl_nb_file_copied.setText(str(self.nb_files_copied))
        self.lbl_nb_files.setFixedWidth(40)
        self.lbl_nb_file_copied.setFixedWidth(40)
        self.lbl_nb_files.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.lbl_nb_file_copied.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)
        # PROGRESS BAR
        self.prg_progress_bar.setFixedHeight(20)
        self.prg_progress_bar.setRange(0, self.nb_files)
        self.prg_progress_bar.setTextVisible(False)

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_name)
        self.main_layout.addWidget(self.prg_progress_bar)
        self.main_layout.addWidget(self.lbl_nb_file_copied)
        self.main_layout.addWidget(self.lbl_slash)
        self.main_layout.addWidget(self.lbl_nb_files)
        self.main_layout.addWidget(self.btn_start)
        self.main_layout.addWidget(self.btn_stop)

    def setup_connections(self):
        self.btn_start.clicked.connect(self.start_copy)
        self.btn_stop.clicked.connect(self.stop_copy)

    def start_copy(self):
        """
        launch all childs copy

        """
        self.btn_start.setVisible(False)
        self.btn_stop.setVisible(True)
        root = self.tree.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if not item.name == self.name:
                continue

            childs = item.childCount()
            for j in range(childs):
                item2 = item.child(j)
                item2.widget.start_copy()

    def stop_copy(self):
        """
        stop all childs copy

        """
        self.btn_start.setVisible(True)
        self.btn_stop.setVisible(False)
        root = self.tree.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            if not item.name == self.name:
                continue

            childs = item.childCount()
            for j in range(childs):
                item2 = item.child(j)
                item2.widget.stop_copy()

class WidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, scene="", name=None, tree_widget=None, parent=None):
        super(WidgetItem, self).__init__()
        self.tree_widget = tree_widget
        self.parent = parent
        self.name = name
        self.scene = scene
        self.main()

    def main(self):
        if self.parent:
            # add child
            self.parent.addChild(self)
            self.widget = little_widget(name=self.name, scene=self.scene, parent=self.parent, tree=self.tree_widget)
            self.tree_widget.setItemWidget(self, 0, self.widget)
        else:
            # add parent
            self.tree_widget.addTopLevelItem(self)
            self.widget = parent_widget(name=self.name, scene=self.scene, tree=self.tree_widget)
            self.tree_widget.setItemWidget(self, 0, self.widget)

class FileCopyerUi(QtWidgets.QDialog):
    def __init__(self):
        super(FileCopyerUi, self).__init__()
        self.setup_ui()
        self.init_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        # BTN
        self.btn_start_all = ActionButtons("")
        self.btn_stop_all = ActionButtons("")
        # COMBO BOX
        self.cb_scene = ComboBox()
        # LABEL
        self.lbl_select_scene = Label("Scene Selection")
        # TREE WIDGET
        self.tw_files = TreeWidget()

    def modify_widgets(self):
        # BTN
        self.btn_start_all.setFixedSize(QtCore.QSize(30, 30))
        self.btn_stop_all.setFixedSize(QtCore.QSize(30, 30))
        self.btn_stop_all.setVisible(False)
        self.btn_start_all.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                            "../../../../resources/icons/play_white.png")))
        self.btn_stop_all.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                           "../../../../resources/icons/pause_white.png")))
        # LABEL
        self.lbl_select_scene.setMaximumWidth(125)

        # TREE WIDGET
        self.tw_files.setSortingEnabled(True)
        self.tw_files.setHeaderLabel("Files To Copy")

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.scene_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.scene_layout.addWidget(self.lbl_select_scene)
        self.scene_layout.addWidget(self.cb_scene)
        self.scene_layout.addWidget(self.btn_start_all)
        self.scene_layout.addWidget(self.btn_stop_all)

        self.main_layout.addLayout(self.scene_layout)
        self.main_layout.addWidget(self.tw_files)

    def setup_connections(self):
        # BTN
        self.btn_start_all.clicked.connect(self.start_all_copy)
        self.btn_stop_all.clicked.connect(self.stop_all_copy)
        # COMBO BOX
        self.cb_scene.currentIndexChanged.connect(self.build_tree)

    def build_tree(self):
        """
        display all the found datas in tree widget

        """
        self.tw_files.clear()
        selected_scene = self.cb_scene.currentText()
        SID_FC = FileCopyer()
        categories = SID_FC.get_all_scene_categories(scene=selected_scene)

        for i in categories:
            current_root = WidgetItem(scene=selected_scene, name=i, tree_widget=self.tw_files)
            child_elements = SID_FC.get_all_scene_category_groups(scene=selected_scene, category=i)
            for j in child_elements:
                WidgetItem(scene=selected_scene, name=j, parent=current_root, tree_widget=self.tw_files)

    def init_ui(self):
        """
        init UI

        """
        self.tw_files.clear()
        self.cb_scene.clear()

        scenes = FileCopyer().get_all_scenes()
        self.cb_scene.addItems(scenes)

    def start_all_copy(self):
        """
        launch all the referenced files

        """
        self.btn_start_all.setVisible(False)
        self.btn_stop_all.setVisible(True)
        root = self.tw_files.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            childs = item.childCount()
            for j in range(childs):
                item2 = item.child(j)
                item2.widget.start_copy()

    def stop_all_copy(self):
        """
        stop all the referenced files

        """
        self.btn_start_all.setVisible(True)
        self.btn_stop_all.setVisible(False)
        root = self.tw_files.invisibleRootItem()
        child_count = root.childCount()
        for i in range(child_count):
            item = root.child(i)
            childs = item.childCount()
            for j in range(childs):
                item2 = item.child(j)
                item2.widget.stop_copy()

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    fenetre = FileCopyerUi()
    fenetre.show()
    app.exec_()