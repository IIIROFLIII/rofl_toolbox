import os

from PySide2 import QtWidgets, QtGui, QtCore

from rofl_toolbox.file_manager.constants import SM_SETTINGS, SOFTWARES, MSG
from rofl_toolbox.generic_python.python_generic import Generic
from rofl_toolbox.data_base_system.sid_bdd_json import SidBdd
from rofl_toolbox.data_base_system.sid_scene_manager_common import SidSceneManagerCommon
from rofl_toolbox.file_manager.widgets.scene_manager.ui.project_widget import AddProject
from rofl_toolbox.file_manager.widgets.scene_manager.ui.scene_widget_add import AddScene
from rofl_toolbox.file_manager.widgets.scene_manager.ui.scene_widget_remove import RemoveScene
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import Label,\
                                                                            ActionButtons,\
                                                                            SmallButtons,\
                                                                            WidgetItem,\
                                                                            TreeWidget,\
                                                                            ComboBox


class little_widget(QtWidgets.QWidget):
    def __init__(self, name="", parent=None, tree=None, file_name=None, api=None, release=False):
        super(little_widget, self).__init__()

        self.tree = tree
        self.parent = parent
        self.parent_name = self.parent.widget.name
        self.name = name
        self.file_name = file_name
        self.api = api
        self.release = release
        self.setup_ui()

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_file_copyer.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self._add_btn_functions()
        self.setup_connections()

    def create_widgets(self):
        self.lbl_name = QtWidgets.QLabel(self.name)

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_name)
        self.main_layout.addStretch()

    def setup_connections(self):
        pass

    def _add_btn_functions(self):
        """
        add buttons behavior to let the user to import or view the files

        """
        if self.parent_name == "caches":
            self._create_import()
            self._create_show_explorer()
            self.main_layout.addWidget(self.btn_import)
            self.main_layout.addWidget(self.btn_show_explorer)
            self.btn_show_explorer.clicked.connect(self.show_explorer)
            self.btn_import.clicked.connect(self.import_cache)

        elif self.parent_name == "flipbooks" or self.parent_name == "wedges" or self.parent_name == "renders":
            self._create_player()
            self._create_import()
            self._create_show_explorer()
            self.main_layout.addWidget(self.btn_player)
            self.main_layout.addWidget(self.btn_import)
            self.main_layout.addWidget(self.btn_show_explorer)
            self.btn_show_explorer.clicked.connect(self.show_explorer)
            self.btn_player.clicked.connect(self.launch_player)
            self.btn_import.clicked.connect(self.import_picture)

            # BUILD CONTEXT MENU
            # set button context menu policy
            self.btn_player.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
            self.btn_player.customContextMenuRequested.connect(self._on_context_menu)
            # create context menu
            self.popMenu = QtWidgets.QMenu(self)
            add_item = QtWidgets.QAction('Add To Rofl Player', self)
            add_items = QtWidgets.QAction('Add All Versions in Rofl Player', self)
            self.popMenu.addAction(add_item)
            self.popMenu.addSeparator()
            self.popMenu.addAction(add_items)
            # connect signals
            add_item.triggered.connect(self.add_item)
            add_items.triggered.connect(self.add_items)

    def _create_import(self):
        """
        import button setup

        """
        self.btn_import = QtWidgets.QPushButton()
        self.btn_import.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                         "../../../../resources/icons/import.png")))
        self.btn_import.setIconSize(QtCore.QSize(15, 15))
        self.btn_import.setFixedSize(QtCore.QSize(25, 25))

    def _create_player(self):
        """
        view pictures setup

        """
        self.btn_player = QtWidgets.QPushButton()
        self.btn_player.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                         "../../../../resources/icons/play.png")))
        self.btn_player.setIconSize(QtCore.QSize(15, 15))
        self.btn_player.setFixedSize(QtCore.QSize(25, 25))

    def _create_show_explorer(self):
        """
        show explorer setup

        """
        self.btn_show_explorer = QtWidgets.QPushButton()
        self.btn_show_explorer.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../../../../resources/icons/folder.png")))
        self.btn_show_explorer.setIconSize(QtCore.QSize(15, 15))
        self.btn_show_explorer.setFixedSize(QtCore.QSize(25, 25))

    def _on_context_menu(self, point):
        # show context menu
        self.popMenu.exec_(self.btn_player.mapToGlobal(point))

    def add_item(self):
        file_path = SidBdd().get_file_path(self.file_name, self.parent_name, self.release)
        file_path = file_path[0].replace("$F4", "0001")
        self.nativeParentWidget().sequence_player.add_file(file_path)

    def add_items(self):
        file_paths = SidBdd().get_all_file_paths(self.file_name, self.parent_name, self.name)
        for file_path in file_paths:
            file_path = file_path.replace("$F4", "0001")
            self.nativeParentWidget().sequence_player.add_file(file_path)

    def import_cache(self):
        file_path = SidBdd().get_file_path(self.file_name, self.parent_name, self.release)
        self.api.import_cache(file_path)

    def import_picture(self):
        file_path = SidBdd().get_file_path(self.file_name, self.parent_name, self.release)[0]
        self.api.import_picture(file_path)

    def launch_player(self):
        extension = os.path.splitext(self.file_name)[-1]
        file_path = SidBdd().get_file_path(self.file_name, self.parent_name, self.release)[0]

        if not os.path.dirname(file_path):
            msg = MSG["NO_SEQUENCE"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False

        if extension == ".exr" and self.api.software == "Houdini":
            self.api.launch_player(file_path)
            return True

        self.add_item()
        self.nativeParentWidget().tab_main.setCurrentIndex(3)

    def show_explorer(self):
        file_path = SidBdd().get_file_path(self.file_name, self.parent_name, self.release)[0]
        folder = os.path.dirname(file_path)
        if not os.path.exists(folder):
            return False

        Generic().open_folder(folder)

class parent_widget(QtWidgets.QWidget):
    def __init__(self, name="", tree=None):
        super(parent_widget, self).__init__()
        self.tree = tree
        self.name = name
        self.setup_ui()

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
        self.lbl_name = QtWidgets.QLabel(self.name)

    def modify_widgets(self):
        pass

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_name)

    def setup_connections(self):
        pass

class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, name=None, tree_widget=None, parent=None, file_name=None, api=None, release=False):
        super(TreeWidgetItem, self).__init__()
        self.tree_widget = tree_widget
        self.parent = parent
        self.name = name
        self.file_name = file_name
        self.api = api
        self.release = release
        self.main()

    def main(self):
        self.setTextColor(0, QtGui.QColor("#fafafa"))
        if self.parent:
            # ADD CHILD ITEMS
            self.parent.addChild(self)
            self.widget = little_widget(name=self.name,
                                        parent=self.parent,
                                        tree=self.tree_widget,
                                        file_name=self.file_name,
                                        api=self.api,
                                        release=self.release)
            self.tree_widget.setItemWidget(self, 0, self.widget)
        else:
            # ADD TOP ITEM
            self.tree_widget.addTopLevelItem(self)
            self.widget = parent_widget(name=self.name, tree=self.tree_widget)
            self.tree_widget.setItemWidget(self, 0, self.widget)

class SceneManager(QtWidgets.QWidget):
    def __init__(self, software):
        super(SceneManager, self).__init__()
        self._init_software = software
        self.software = software
        self.setup_ui()
        self._init_ui()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.modify_layout()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        # BTN
        self.btn_load = ActionButtons("Open Scene")
        self.btn_modify_path = ActionButtons("...")
        self.btn_name_add = SmallButtons("+")
        self.btn_name_remove = SmallButtons("-")
        self.btn_project_add = SmallButtons("+")
        self.btn_project_remove = SmallButtons("-")
        self.btn_save_export = ActionButtons("Save / Export")
        self.btn_show_explorer = QtWidgets.QPushButton()
        self.btn_step_add = SmallButtons("+")
        self.btn_step_remove = SmallButtons("-")
        self.btn_task_add = SmallButtons("+")
        self.btn_task_remove = SmallButtons("-")
        # COMBO BOX
        self.cb_soft_filter = ComboBox()
        self.cb_project = ComboBox()
        # LABELS
        self.lbl_soft_filter = Label("Software Filter")
        self.lbl_project = Label("Select Project")
        self.lbl_name = Label("Name")
        self.lbl_task = Label("Task")
        self.lbl_step = Label("Step")
        self.lbl_scene = Label("Scene")
        self.lbl_file = Label("Files")
        self.lbl_commentaries = Label("Commentaries")
        # LINE EDIT
        self.le_commentaries = QtWidgets.QTextEdit()
        # LIST WIDGET
        self.lw_name = QtWidgets.QListWidget()
        self.lw_task = QtWidgets.QListWidget()
        self.lw_step = QtWidgets.QListWidget()
        self.lw_version = QtWidgets.QListWidget()
        self.lw_version_release = QtWidgets.QListWidget()
        # TOOL BOX
        self.tb_scene = QtWidgets.QToolBox()
        # TREE WIDGET
        self.tw_file = TreeWidget()

    def modify_widgets(self):
        # BTN
        self.btn_load.setFixedHeight(30)
        self.btn_modify_path.setObjectName("smallSize")
        self.btn_modify_path.setFixedSize(QtCore.QSize(32, 18))
        self.btn_modify_path.setToolTip("Modify Projects Root Path")
        self.btn_save_export.setFixedHeight(30)
        self.btn_show_explorer.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../../../../resources/icons/folder.png")))
        self.btn_show_explorer.setIconSize(QtCore.QSize(20, 20))
        self.btn_show_explorer.setFixedSize(QtCore.QSize(30, 30))
        # COMBO BOX
        self.cb_soft_filter.setMaximumWidth(120)
        # LINE EDIT
        self.le_commentaries.setReadOnly(True)
        self.le_commentaries.setMaximumHeight(200)
        # LIST WIDGET
        self.lw_name.setIconSize(QtCore.QSize(20, 20))
        self.lw_name.setMaximumWidth(180)
        self.lw_step.setIconSize(QtCore.QSize(20, 20))
        self.lw_step.setMaximumWidth(180)
        self.lw_task.setIconSize(QtCore.QSize(20, 20))
        self.lw_task.setMaximumWidth(180)
        self.lw_version.setIconSize(QtCore.QSize(17, 17))
        self.lw_version_release.setIconSize(QtCore.QSize(17, 17))
        # TOOL BOX
        self.tb_scene.setMinimumWidth(325)
        self.tb_scene.addItem(self.lw_version, "WORK")
        self.tb_scene.addItem(self.lw_version_release, "RELEASE")
        # TREE WIDGET
        self.tw_file.setIconSize(QtCore.QSize(17, 17))
        self.tw_file.setSortingEnabled(True)
        self.tw_file.setHeaderLabel("")
        self.tw_file.setHeaderHidden(True)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.file_layout = QtWidgets.QVBoxLayout()
        self.liste_layout = QtWidgets.QHBoxLayout()
        self.name_layout = QtWidgets.QVBoxLayout()
        self.name_title_layout = QtWidgets.QHBoxLayout()
        self.project_layout = QtWidgets.QHBoxLayout()
        self.scene_action_layout = QtWidgets.QHBoxLayout()
        self.scene_list_layout = QtWidgets.QHBoxLayout()
        self.scene_layout = QtWidgets.QVBoxLayout()
        self.step_layout = QtWidgets.QVBoxLayout()
        self.step_title_layout = QtWidgets.QHBoxLayout()
        self.task_layout = QtWidgets.QVBoxLayout()
        self.task_title_layout = QtWidgets.QHBoxLayout()
        self.version_layout = QtWidgets.QVBoxLayout()

    def modify_layout(self):
        self.lbl_project.setContentsMargins(0, 0, 10, 0)
        self.name_layout.setContentsMargins(0, 0, 5, 0)
        self.project_layout.setContentsMargins(0, 10, 0, 15)
        self.step_layout.setContentsMargins(0, 0, 5, 0)
        self.task_layout.setContentsMargins(0, 0, 5, 0)

    def add_widgets_to_layouts(self):
        # HEADER PROJECT
        self.project_layout.addWidget(self.lbl_project)
        self.project_layout.addWidget(self.cb_project)
        self.project_layout.addWidget(self.btn_project_add)
        self.project_layout.addWidget(self.btn_project_remove)
        self.project_layout.addWidget(self.btn_modify_path)
        self.project_layout.addStretch()
        self.project_layout.addWidget(self.lbl_soft_filter)
        self.project_layout.addWidget(self.cb_soft_filter)
        # HEADER NAME
        self.name_title_layout.addWidget(self.lbl_name)
        self.name_title_layout.addWidget(self.btn_name_add)
        self.name_title_layout.addWidget(self.btn_name_remove)
        # HEADER TASK
        self.task_title_layout.addWidget(self.lbl_task)
        self.task_title_layout.addWidget(self.btn_task_add)
        self.task_title_layout.addWidget(self.btn_task_remove)
        # HEADER STEP
        self.step_title_layout.addWidget(self.lbl_step)
        self.step_title_layout.addWidget(self.btn_step_add)
        self.step_title_layout.addWidget(self.btn_step_remove)
        # BUTTONS SCENES
        self.scene_action_layout.addWidget(self.btn_load)
        self.scene_action_layout.addWidget(self.btn_save_export)
        self.scene_action_layout.addWidget(self.btn_show_explorer)
        # COLUMN NAME
        self.name_layout.addLayout(self.name_title_layout)
        self.name_layout.addWidget(self.lw_name)
        # COLUMN TASK
        self.task_layout.addLayout(self.task_title_layout)
        self.task_layout.addWidget(self.lw_task)
        # COLUMN STEP
        self.step_layout.addLayout(self.step_title_layout)
        self.step_layout.addWidget(self.lw_step)
        # SCENE BOX
        self.version_layout.addWidget(self.lbl_scene)
        self.version_layout.addWidget(self.tb_scene)
        # FILES BOX
        self.file_layout.addWidget(self.lbl_file)
        self.file_layout.addWidget(self.tw_file)
        # SCENE AND FILES BOX
        self.scene_list_layout.addLayout(self.version_layout)
        self.scene_list_layout.addLayout(self.file_layout)
        # COLUMN SCENES
        self.scene_layout.addLayout(self.scene_list_layout)
        self.scene_layout.addWidget(self.lbl_commentaries)
        self.scene_layout.addWidget(self.le_commentaries)
        self.scene_layout.addLayout(self.scene_action_layout)
        # GLOBAL BOX BOTTOM
        self.liste_layout.addLayout(self.name_layout)
        self.liste_layout.addLayout(self.task_layout)
        self.liste_layout.addLayout(self.step_layout)
        self.liste_layout.addLayout(self.scene_layout)
        # PROJECT AND GLOBAL
        self.main_layout.addLayout(self.project_layout)
        self.main_layout.addLayout(self.liste_layout)

    def setup_connections(self):
        # BTN
        self.btn_load.clicked.connect(self.load_scene)
        self.btn_modify_path.clicked.connect(self.modify_path)
        self.btn_name_add.clicked.connect(self.add_name)
        self.btn_name_remove.clicked.connect(self.delete_name)
        self.btn_project_add.clicked.connect(self.add_project)
        self.btn_project_remove.clicked.connect(self.delete_project)
        self.btn_save_export.clicked.connect(self.save_scene)
        self.btn_show_explorer.clicked.connect(self.show_explorer)
        self.btn_step_add.clicked.connect(self.add_step)
        self.btn_step_remove.clicked.connect(self.delete_step)
        self.btn_task_add.clicked.connect(self.add_task)
        self.btn_task_remove.clicked.connect(self.delete_task)
        # COMBO BOX
        self.cb_project.currentIndexChanged.connect(self.selection_project)
        self.cb_soft_filter.currentIndexChanged.connect(self._software_filter)
        # LIST WIDGET
        self.lw_name.currentRowChanged.connect(self.selection_name)
        self.lw_step.currentRowChanged.connect(self.selection_step)
        self.lw_task.currentRowChanged.connect(self.selection_task)
        self.lw_version.currentRowChanged.connect(self.selection_version)
        self.lw_version_release.currentRowChanged.connect(self.selection_version_release)
        # TOOLBOX
        self.tb_scene.currentChanged.connect(self.selection_toolbox)

    def _add_name_item(self, item=None):
        """
        add given name project to the list name project display
        Args:
            item: name of the project name

        """
        self.lw_name.clear()
        # get project names from database and fill list widget
        name_list = self.bdd.get_scenes_name_list(software=self.software)
        if item:
            name_list.append(item)
        for name in sorted(set(name_list)):
            WidgetItem(name=name, list_widget=self.lw_name)

        # set selection on the new name project
        for i in range(self.lw_name.count()):
            lw_item = self.lw_name.item(i)
            if lw_item.name == item:
                self.lw_name.setCurrentRow(i)

        self.bdd.SID = self._sid_generator()

    def _add_task_item(self, item=None):
        """
        add given task project to the list task project display
        Args:
            item: name of the project task

        """
        self.lw_task.clear()
        # get project tasks from database and fill list widget
        task_list = self.bdd.get_scenes_task_list(software=self.software)
        if item:
            task_list.append(item)
        for task in sorted(set(task_list)):
            WidgetItem(name=task, list_widget=self.lw_task)

        # set selection
        for i in range(self.lw_task.count()):
            lw_item = self.lw_task.item(i)
            if lw_item.name == item:
                self.lw_task.setCurrentRow(i)

        self.bdd.SID = self._sid_generator()

    def _add_step_item(self, item=None):
        """
        add given step project to the list step project display
        Args:
            item: name of the project step

        """
        self.lw_step.clear()
        # get project steps from database and fill list widget
        step_list = self.bdd.get_scenes_step_list(software=self.software)
        if item:
            step_list.append(item)
        for step in sorted(set(step_list)):
            WidgetItem(name=step, list_widget=self.lw_step)

        # set selection
        for i in range(self.lw_step.count()):
            lw_item = self.lw_step.item(i)
            if lw_item.name == item:
                self.lw_step.setCurrentRow(i)

        self.bdd.SID = self._sid_generator()

    def _add_version_item(self, list_widget=None, release=False):
        """
        add versions according to elements selection on version project display
        Args:
            list_widget: which list widget to display
            release: lokking for release scene

        """
        list_widget.clear()
        # get project scenes from database and fill list widget
        version_list = self.bdd.get_scenes_filename_list_with_software(software=self.software, release=release)
        for software, file in sorted(set(version_list)):
            WidgetItem(name=file, icon=software, list_widget=list_widget)

        self.bdd.SID = self._sid_generator()

    def _build_tree(self, release=False):
        """
        display all the files according to the scene selection
        Args:
            files: files found in the database

        """
        files = self.bdd.get_files(release=release)
        self.tw_file.clear()
        categories = self.bdd.get_all_files_category(files=files)
        release = True if self.tb_scene.currentIndex() else False
        for category in categories:
            current_root = TreeWidgetItem(name=category, tree_widget=self.tw_file)

            child_elements = self.bdd.get_all_files_category_childs(files=files, category=category)
            for child in child_elements:
                file_name = self.bdd.get_child_file_name(files=files, category=category, child=child)
                TreeWidgetItem(name=child,
                               parent=current_root,
                               tree_widget=self.tw_file,
                               file_name=file_name,
                               api=self._load_software_api(),
                               release=release)

    def _check_project_selection(self):
        """
        check if a project is selected
        Returns: True if succeed

        """
        if not self.cb_project.currentText():
            msg = MSG["SELECT_PROJECT"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False
        return True

    def _check_name_selection(self):
        """
        check if a name project is selected
        Returns: True if succeed

        """
        if self.lw_name.currentRow() == -1:
            msg = MSG["SELECT_NAME"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False
        return True

    def _check_task_selection(self):
        """
        check if a task project is selected
        Returns: True if succeed

        """
        if self.lw_task.currentRow() == -1:
            msg = MSG["SELECT_TASK"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False
        return True

    def _check_software(self):
        """
        check if the selected scene is compatible whith the current software used
        Returns: True if succeed

        """
        if not self._init_software == self.software:
            msg = MSG["SOFTWARE_NOT_CONFORM"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False
        return True

    def _check_step_selection(self):
        """
        check if a step project is selected
        Returns: True if succeed

        """
        if self.lw_step.currentRow() == -1:
            msg = MSG["SELECT_STEP"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False
        return True

    def _check_version_selection(self):
        """
        check if a version project is selected
        Returns: True if succeed

        """
        if self.lw_version.currentRow() == -1:
            msg = MSG["SELECT_SCENE"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False
        return True

    def _check_complete(self):
        """
        check all steps
        Returns: True if succeed

        """
        if not self._check_project_selection():
            return False
        if not self._check_name_selection():
            return False
        if not self._check_task_selection():
            return False
        if not self._check_step_selection():
            return False
        return True

    def _delete_list_widget_item(self, type, list_widget):
        """
        delete the selected item in the given list widget and remove in database too
        Args:
            type: the type of the data to remove
            list_widget: the list widget to remove item from

        """
        result = self._remove_datas()
        if not result:
            return False

        sid_actions = SidSceneManagerCommon(sid=self._sid_generator())
        if not sid_actions.remove_datas(result, software=self.software, type=type):
            return False

        selection = self._get_selected_lw_item(list_widget)
        list_widget.takeItem(list_widget.row(selection))

    def _get_selected_lw_item(self, lw):
        """
        check if an item is selected in the given list widget
        Args:
            lw: the list widget to check

        Returns: the selection

        """
        selected_items = lw.selectedItems()
        if selected_items:
            return selected_items[0]
        return None

    def _get_user_input(self):
        """
        collect all the widgets selection
        Returns: a list of the widgets selection

        """
        project = name = task = step = version = SidBdd().SID_base

        if self.cb_project.currentText() != "":
            project = self.cb_project.currentText()

        if not self.lw_name.currentRow() == -1:
            name = self.lw_name.currentItem().text()

        if not self.lw_task.currentRow() == -1:
            task = self.lw_task.currentItem().text()

        if not self.lw_step.currentRow() == -1:
            step = self.lw_step.currentItem().text()

        if not self.tb_scene.currentIndex():
            if not self.lw_version.currentRow() == -1:
                selected_scene = self.lw_version.currentItem().text()
                selected_sid = SidBdd().conform_file_for_sid(file=selected_scene)
                selected_version = SidBdd(sid=selected_sid).SID_version
                version = selected_version
        else:
            if not self.lw_version_release.currentRow() == -1:
                selected_scene = self.lw_version_release.currentItem().text()
                selected_sid = SidBdd().conform_file_for_sid(file=selected_scene)
                selected_version = SidBdd(sid=selected_sid).SID_version
                version = selected_version

        return [project, name, task, step, version]

    def _init_ui(self):
        """
        init UI with all the available elements

        """
        # apply filter software
        self.cb_soft_filter.addItems(SOFTWARES)
        self._set_software_filter(self._init_software)
        # generate settings json if not exist
        if not os.path.exists(SM_SETTINGS):
            self._settings_save({})
        # refresh data and apply settings
        data = self._settings_read()
        self._refresh_projects()
        self._settings_apply(data)

    def _load_software_api(self):
        """
        load software file manager api
        Returns: True if succeed

        """
        if self._init_software == "Houdini":
            from rofl_toolbox.file_manager.widgets.scene_manager.api.SM_houdini import SceneManagerHoudini
            fmActions = SceneManagerHoudini(self._sid_generator())
            return fmActions
        else:
            msg = MSG["SOFTWARE_NOT_MANAGE"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return None

    def _refresh_projects(self):
        """
        refresh projects list from database
        """
        self.cb_project.clear()
        project_list = SidBdd()._get_project_list()
        if len(project_list):
            self.cb_project.addItems(sorted(set(project_list)))
            self.bdd = SidBdd(self._sid_generator())

    def _remove_datas(self):
        """
        load little UI to give user the choice of deletion
        Returns: the choice of the user

        """
        fenetre = RemoveScene()
        fenetre.show()
        fenetre.exec_()

        result = None
        if fenetre.data_and_files:
            result = "DB and Files"
        elif fenetre.datas:
            result = "DB"

        return result

    def _set_project_with_alias(self, alias):
        """
        set project whith the given alias
        Args:
            alias: th alias project to looking for
        """
        index = self.cb_project.findText(alias, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cb_project.setCurrentIndex(index)

    def _set_software_filter(self, software):
        """
        set software filer at init UI
        Args:
            software: the software name to set software filter with

        """
        index = self.cb_soft_filter.findText(software, QtCore.Qt.MatchFixedString)
        if index >= 0:
            self.cb_soft_filter.setCurrentIndex(index)

    def _settings_apply(self, data):
        """
        apply the settings previously saved
        Args:
            data: the widgets selection list

        """
        project = data.get("project")
        name = data.get("name")
        task = data.get("task")
        step = data.get("step")
        toolbox = data.get("toolbox")
        version = data.get("version")
        version_release = data.get("version_release")
        if project:
            self._set_project_with_alias(project)
        if name != -1 and name != None:
            self.lw_name.setCurrentRow(name)
        if task != -1 and task != None:
            self.lw_task.setCurrentRow(task)
        if step != -1 and step != None:
            self.lw_step.setCurrentRow(step)
        if toolbox:
            self.tb_scene.setCurrentIndex(toolbox)

        if version != -1 and version != None and self.tb_scene.currentIndex() == 0:
            self.lw_version.setCurrentRow(version)
        if version_release != -1 and version_release != None and self.tb_scene.currentIndex() == 1:
            self.lw_version_release.setCurrentRow(version_release)

    def _settings_read(self):
        """
        load UI previous settings
        Returns: the previous settings after user quit the UI

        """
        datas = Generic().read_json(data_file=SM_SETTINGS)
        return datas

    def _settings_save(self, data):
        """
        save UI current settings
        Args:
            data: the datas to save (which are widgets selection)

        """
        Generic().save_json(data_file=SM_SETTINGS, data=data)

    def _settings_save_parameters(self):
        """
        save the elements selection in file to retrieve it at filemanager restart

        """
        datas = self._settings_read()
        datas.update({"project": self.cb_project.currentText()})
        datas.update({"name": self.lw_name.currentRow()})
        datas.update({"task": self.lw_task.currentRow()})
        datas.update({"step": self.lw_step.currentRow()})
        datas.update({"toolbox": self.tb_scene.currentIndex()})
        datas.update({"version": self.lw_version.currentRow()})
        datas.update({"version_release": self.lw_version_release.currentRow()})

        self._settings_save(datas)

    def _sid_generator(self):
        """
        generate a SID for database system according to the widgets selection
        Returns:

        """
        user_data = self._get_user_input()
        return SidBdd().build_SID(user_data)

    def _software_filter(self):
        """
        define which scenes to display according to the selected software
        Returns:

        """
        filter = self.cb_soft_filter.currentText()
        self.software = filter if filter != "None" else None

    def add_project(self):
        """
        add projects in project combo box menu
        """
        fenetre = AddProject()
        fenetre.show()
        fenetre.exec_()
        if not fenetre.alias:
            return False

        # add project in database system
        creation, log = SidBdd(fenetre.alias).create_project(fenetre.alias, fenetre.path)
        if not creation:
            self.nativeParentWidget().statusBar.showMessage(log, 10000)
            return False

        self._refresh_projects()
        self._set_project_with_alias(fenetre.alias)

    def add_name(self):
        """
        add name project in the accoridng list widget
        """
        if not self._check_project_selection():
            return False

        fenetre = AddScene(name=True, task=True, step=True)
        fenetre.show()
        fenetre.exec_()
        if not fenetre.name_info:
            return False

        self._add_name_item(item=fenetre.name_info)
        self._add_task_item(item=fenetre.task_info)
        self._add_step_item(item=fenetre.step_info)

    def add_task(self):
        """
        add task project in the accoridng list widget
        """
        if not self._check_project_selection():
            return False
        if not self._check_name_selection():
            return False

        fenetre = AddScene(task=True, step=True)
        fenetre.show()
        fenetre.exec_()
        if not fenetre.task_info:
            return False

        self._add_task_item(item=fenetre.task_info)
        self._add_step_item(item=fenetre.step_info)

    def add_step(self):
        """
        add step project in the accoridng list widget
        """
        if not self._check_project_selection():
            return False
        if not self._check_name_selection():
            return False
        if not self._check_task_selection():
            return False

        fenetre = AddScene(step=True)
        fenetre.show()
        fenetre.exec_()
        if not fenetre.step_info:
            return False

        self._add_step_item(item=fenetre.step_info)

    def delete_project(self):
        """
        delete the selected project in explorer and database according to the choice of the user

        """
        if not self._check_project_selection():
            return False
        result = self._remove_datas()
        if not result:
            return False

        sid_actions = SidSceneManagerCommon(sid=self._sid_generator())
        if not sid_actions.remove_datas(result, software=self.software, type="Project"):
            return False

        self._refresh_projects()

    def delete_name(self):
        """
        delete the selected project name in explorer and database according to the choice of the user

        """
        if not self._check_project_selection():
            return False
        if not self._check_name_selection():
            return False

        self._delete_list_widget_item(type="Name", list_widget=self.lw_name)

    def delete_task(self):
        """
        delete the selected project task in explorer and database according to the choice of the user

        """
        if not self._check_project_selection():
            return False
        if not self._check_name_selection():
            return False
        if not self._check_task_selection():
            return False

        self._delete_list_widget_item(type="Task", list_widget=self.lw_task)

    def delete_step(self):
        """
        delete the selected project step in explorer and database according to the choice of the user

        """
        if not self._check_project_selection():
            return False
        if not self._check_name_selection():
            return False
        if not self._check_task_selection():
            return False
        if not self._check_step_selection():
            return False

        self._delete_list_widget_item(type="Step", list_widget=self.lw_step)

    def modify_path(self):
        selected_project = self.cb_project.currentText()
        if not selected_project:
            return False

        current_root = SidBdd(sid=selected_project).project_root
        fenetre = AddProject()
        fenetre.le_alias.setText(selected_project)
        fenetre.le_alias.setDisabled(True)
        fenetre.le_path.setText(current_root)
        fenetre.show()
        fenetre.exec_()
        if not fenetre.alias:
            return False

        SID = self._sid_generator()
        BDD_SID = SidBdd(SID)
        BDD_SID.modify_project_root(path=fenetre.path)

    def selection_project(self):
        """
        display name elements with the selected project

        """
        self.bdd = SidBdd(self._sid_generator())
        self._add_name_item()
        self._settings_save_parameters()

    def selection_name(self):
        """
        display task elements with the selected name

        """
        self.bdd = SidBdd(self._sid_generator())
        self._add_task_item()
        self._settings_save_parameters()

    def selection_task(self):
        """
        display step elements with the selected task

        """
        self.bdd = SidBdd(self._sid_generator())
        self._add_step_item()
        self._settings_save_parameters()

    def selection_step(self):
        """
        display version elements with the selected step

        """
        self.bdd = SidBdd(self._sid_generator())
        self._add_version_item(list_widget=self.lw_version)
        self._add_version_item(list_widget=self.lw_version_release, release=True)
        self._settings_save_parameters()

    def selection_toolbox(self):
        """
        display scenes according to the toolbox selection

        """
        self.tw_file.clear()
        if self.tb_scene.currentIndex() == 0:
            self.selection_version()
        else:
            self.selection_version_release()
        self._settings_save_parameters()

    def selection_version(self):
        """
        display scene infos with the selected version

        """
        self.bdd = SidBdd(self._sid_generator())
        self.le_commentaries.setPlainText(self.bdd.get_commentary())
        self._build_tree()
        self._settings_save_parameters()

    def selection_version_release(self):
        """
        display scene release infos with the selected version

        """
        self.bdd = SidBdd(self._sid_generator())
        self.le_commentaries.setPlainText(self.bdd.get_commentary())
        self._build_tree(release=True)
        self._settings_save_parameters()

    def load_scene(self):
        """
        load the selected scene

        """
        if not self._check_software():
            return False
        if not self._check_complete():
            return False
        if self.lw_version.currentRow() == -1 and self.lw_version_release.currentRow() == -1:
            msg = MSG["SELECT_SCENE"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False

        api = self._load_software_api()
        if not api:
            return False

        success, log = api.open(release=self.tb_scene.currentIndex())
        if not success:
            self.nativeParentWidget().statusBar.showMessage(log, 10000)
            return False

    def save_scene(self):
        """
        save scene and copy files if necessary

        """
        if not self._check_software():
            return False
        if not self._check_complete():
            return False

        # api loading
        api = self._load_software_api()
        if not api:
            return False

        # api save execution
        success, log = api.save()
        if not success:
            self.nativeParentWidget().statusBar.showMessage(log, 10000)
            return False

        # reload version list widget
        self.selection_step()
        self.lw_version.setCurrentRow(0)

        # check if there is files to copy
        if not api.files_to_copy:
            return False
        # launch copy process
        self.nativeParentWidget().tab_main.setCurrentIndex(1)
        self.nativeParentWidget().file_copyer.init_ui()
        self.nativeParentWidget().file_copyer.start_all_copy()

    def show_explorer(self):
        """
        open an os explorer according to the current widgets selection

        """
        # get all widgets selections
        prj = True if self.cb_project.currentText() else False
        name = True if not self.lw_name.currentRow() == -1 else False
        task = True if not self.lw_task.currentRow() == -1 else False
        step = True if not self.lw_step.currentRow() == -1 else False
        version = True if not self.lw_version.currentRow() == -1 else False
        version_release = True if not self.lw_version_release.currentRow() == -1 else False

        # open explorer on work or release folder
        if self.tb_scene.currentIndex() == 0:
            if prj and name and task and step and version:
                path = self.bdd.SID_scene_folder()
                Generic().open_folder(path)
                return True
        else:
            if prj and name and task and step and version_release:
                path = self.bdd.SID_release_scene_folder()
                Generic().open_folder(path)
                return True

        # open explorer on name or taks or step folder
        if prj and name and task and step:
            path = self.bdd.SID_scene_step_folder()
        elif prj and name and task:
            path = self.bdd.SID_task_folder()
        elif prj and name:
            path = self.bdd.SID_name_folder()
        elif prj:
            path = self.bdd.project_root
        else:
            path = ""
        Generic().open_folder(path)

if __name__ == '__main__':
    app = QtWidgets.QApplication()
    fenetre = SceneManager(software="Python")
    fenetre.show()
    app.exec_()