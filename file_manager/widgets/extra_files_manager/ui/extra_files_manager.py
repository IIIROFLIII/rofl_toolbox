import os

from PySide2 import QtWidgets, QtCore, QtGui

from rofl_toolbox.generic_python.python_generic import Generic
from rofl_toolbox.file_manager.constants import MSG
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import TreeWidget, ActionButtons, Label

COLORS = {False: (91, 231, 155), True: (231, 112, 91)}

class ParmItem(QtWidgets.QListWidgetItem):
    def __init__(self, parm_path, state, list_widget):
        super(ParmItem, self).__init__(parm_path)
        self.list_widget = list_widget
        self.state = state
        self.parm_path = parm_path

        self.setSizeHint(QtCore.QSize(self.sizeHint().width(), 25))
        self.list_widget.addItem(self)
        self.set_color_text()

    def set_color_text(self):
        color = COLORS.get(self.state)
        self.setTextColor(QtGui.QColor(*color))

class little_widget(QtWidgets.QWidget):
    def __init__(self, name="",
                 parent_widget=None,
                 tree=None,
                 api=None):

        super(little_widget, self).__init__()

        self.tree = tree
        self.parent_widget = parent_widget
        self.parent_name = self.parent_widget.widget.name
        self.name = name
        self.api = api
        self.setup_ui()

    @property
    def files_source(self):
        """
        get all the files according to the item
        Returns: a list of files source

        """
        return self.api.get_files_source(self.parent_name, self.name)

    @property
    def folder_path(self):
        """
        get the folder path which contain the files of the item
        Returns: the folder path

        """
        return self.api.get_folder_path(self.parent_name, self.name)

    @property
    def is_allowed(self):
        """
        tell if the category is allowed to be copied
        Returns: True if succeed

        """
        return self.api.get_extension_authorization(self.parent_name)

    @property
    def parms(self):
        """
        get all the parms path according to the item file
        Returns: list of parms path

        """
        return self.api.get_parms_path(self.parent_name, self.name)

    @property
    def weight(self):
        """
        get the weight of all the files
        Returns: the files weight in human readable

        """
        weight = self.api.get_weight(self.parent_name, self.name)
        return Generic().human_bytes(weight)

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
        self.lbl_weight = QtWidgets.QLabel(self.weight)
        self.btn_show_explorer = ActionButtons("")

    def modify_widgets(self):
        if self.is_allowed:
            self.lbl_name.setObjectName("IsValid")
        else:
            self.lbl_name.setObjectName("IsNotValid")

        self.btn_show_explorer.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                                "../../../../resources/icons/folder.png")))
        self.btn_show_explorer.setIconSize(QtCore.QSize(17, 17))
        self.btn_show_explorer.setFixedSize(QtCore.QSize(22, 22))
        if not self.folder_path:
            self.btn_show_explorer.setDisabled(True)

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_name)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.lbl_weight)
        self.main_layout.addWidget(self.btn_show_explorer)

    def setup_connections(self):
        self.btn_show_explorer.clicked.connect(self.show_explorer)

    def show_explorer(self):
        """
        open explorer os on the folder directory

        """
        if not os.path.exists(self.folder_path):
            return False

        Generic().open_folder(self.folder_path)

class parent_widget(QtWidgets.QWidget):
    def __init__(self, name="", tree=None, api=None):
        super(parent_widget, self).__init__()
        self.parent_widget = None
        self.tree = tree
        self.name = name
        self.api = api
        self.setup_ui()

    @property
    def is_allowed(self):
        """
        tell if the category is allowed to be copied
        Returns: True if succeed

        """
        return self.api.get_extension_authorization(self.name)

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
        if self.is_allowed:
            self.lbl_name.setObjectName("IsValid")
        else:
            self.lbl_name.setObjectName("IsNotValid")

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_name)

    def setup_connections(self):
        pass

class TreeWidgetItem(QtWidgets.QTreeWidgetItem):
    def __init__(self, tree_widget=None, name=None,
                 parent=None, api=None):

        super(TreeWidgetItem, self).__init__()
        self.tree_widget = tree_widget
        self.name = name
        self.parent = parent
        self.api = api
        self.main()

    def add_child(self):
        self.parent.addChild(self)
        self.widget = little_widget(name=self.name, parent_widget=self.parent, tree=self.tree_widget, api=self.api)

        self.tree_widget.setItemWidget(self, 0, self.widget)

    def add_parent(self):
        self.setFlags(self.flags() & ~QtCore.Qt.ItemIsSelectable)
        self.tree_widget.addTopLevelItem(self)
        self.widget = parent_widget(tree=self.tree_widget, name=self.name, api=self.api)
        self.tree_widget.setItemWidget(self, 0, self.widget)

    def main(self):
        if self.parent:
            self.add_child()
        else:
            self.add_parent()

class ExtraFilesManagerUi(QtWidgets.QWidget):
    def __init__(self, software=None):
        super(ExtraFilesManagerUi, self).__init__()
        self.software = software
        self.setup_ui()
        self.api = self._load_software_api()

    def setup_ui(self):
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.modify_layout()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        # BTN
        self.btn_get = ActionButtons("Get Files")
        self.btn_refresh = ActionButtons("Refresh")
        # LABEL
        self.lbl_parms_path = Label("Parms Path")
        self.lbl_scene_files = Label("Scene Files")
        self.lbl_files_weight = QtWidgets.QLabel("Global Weight: 0.0 Byte")
        self.lbl_copy_allowed = QtWidgets.QLabel("Copy Allowed")
        self.lbl_copy_not_allowed = QtWidgets.QLabel("Copy Not Allowed")
        self.lbl_parm_repathable = QtWidgets.QLabel("Parm Repathable")
        self.lbl_parm_not_repathable = QtWidgets.QLabel("Parm Not Repathable")
        # LIST WIDGET
        self.lw_parms = QtWidgets.QListWidget()
        # TREE WIDGET
        self.tw_extra_files = TreeWidget()

    def modify_widgets(self):
        # BTN
        self.btn_get.setMinimumHeight(40)
        self.btn_refresh.setMinimumHeight(40)
        self.btn_get.setMinimumWidth(100)
        self.btn_refresh.setMinimumWidth(100)

        # LIST WIDGET
        self.lw_parms.setMaximumWidth(400)
        # TREE WIDGET
        self.tw_extra_files.setMaximumWidth(100000)
        self.tw_extra_files.setHeaderLabel("Extra Files")
        self.tw_extra_files.setObjectName("IsSelectable")
        self.tw_extra_files.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        # LABEL
        self.lbl_copy_allowed.setObjectName("IsValid")
        self.lbl_copy_not_allowed.setObjectName("IsNotValid")
        self.lbl_parm_repathable.setObjectName("IsValid")
        self.lbl_parm_not_repathable.setObjectName("IsNotValid")

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.lists_layout = QtWidgets.QHBoxLayout()

    def modify_layout(self):
        pass

    def add_widgets_to_layouts(self):
        self.header_layout.addWidget(self.lbl_scene_files)
        self.header_layout.addWidget(self.lbl_copy_allowed)
        self.header_layout.addWidget(self.lbl_copy_not_allowed)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.btn_refresh)
        self.header_layout.addWidget(self.btn_get)
        self.header_layout.addStretch()
        self.header_layout.addWidget(self.lbl_parm_repathable)
        self.header_layout.addWidget(self.lbl_parm_not_repathable)
        self.header_layout.addWidget(self.lbl_parms_path)

        self.lists_layout.addWidget(self.tw_extra_files)
        self.lists_layout.addWidget(self.lw_parms)

        self.btn_layout.addWidget(self.lbl_files_weight)
        self.btn_layout.addStretch()

        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.lists_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        # BTN
        self.btn_get.clicked.connect(self.get_files)
        self.btn_refresh.clicked.connect(self.refresh_files)
        # TREE WIDGET
        self.tw_extra_files.itemSelectionChanged.connect(self.fill_list_infos)
        # LIST WIDGET
        self.lw_parms.itemSelectionChanged.connect(self.select_parm_node)

    def _build_tree(self):
        """
        build tree according to api database

        """
        self.tw_extra_files.clear()
        categories = self.api.get_all_categories()

        for category in categories:
            current_root = TreeWidgetItem(tree_widget=self.tw_extra_files, name=category, api=self.api)
            if current_root.widget.is_allowed:
                self.tw_extra_files.expandItem(current_root)

            files = self.api.get_all_category_files(category=category)
            for file in files:
                TreeWidgetItem(tree_widget=self.tw_extra_files, name=file, parent=current_root, api=self.api)

    def _load_software_api(self):
        """
        load the api according to the launching software

        """
        if self.software == "Houdini":
            from rofl_toolbox.file_manager.widgets.extra_files_manager.api.EFM_houdini import EfmHoudini
            efmActions = EfmHoudini()
            return efmActions
        else:
            msg = MSG["SOFTWARE_NOT_MANAGE"]
            if self.nativeParentWidget():
                self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return None

    def fill_list_infos(self):
        """
        fill list_widget with parms path according to the file selection
        modify the global weight too

        """
        self.lw_parms.clear()
        self.lbl_files_weight.setText("0.0 Bytes")
        selected_items = self.tw_extra_files.selectedItems()
        if not selected_items:
            return False

        weights = 0.0
        items = [item for item in selected_items if item.widget.parent_widget]
        for item in items:
            parms = item.widget.parms
            for parm_path, state in parms:
                ParmItem(parm_path=parm_path, state=state, list_widget=self.lw_parms)

            item_parent_name = item.widget.parent_name
            item_name = item.widget.name
            weights += item.api.get_weight(item_parent_name, item_name)

        self.lbl_files_weight.setText("Global Weight: " + Generic().human_bytes(weights))

    def get_files(self):
        """
        copy selected files and repath parm scene

        """
        selected_items = self.tw_extra_files.selectedItems()
        if not selected_items:
            return False

        self.api.get_files(selected_items)
        self.api.repathing_parms(selected_items)
        if not self.api.files_to_copy:
            return False

        self.nativeParentWidget().tab_main.setCurrentIndex(1)
        self.nativeParentWidget().file_copyer.init_ui()
        self.nativeParentWidget().file_copyer.start_all_copy()
        self.tw_extra_files.clear()

    def refresh_files(self):
        """
        get all the extra files of the current scene and build the tree widget

        """
        self.api.refresh_files()
        self._build_tree()

    def select_parm_node(self):
        """
        select the node which contain the selected parm

        """
        selected_items = self.lw_parms.selectedItems()
        if not selected_items:
            return False

        item = selected_items[0]
        self.api.select_parm_node(item.parm_path)

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    fenetre = ExtraFilesManagerUi()
    fenetre.show()
    app.exec_()