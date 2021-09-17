import os
import hou

from PySide2 import QtWidgets, QtCore, QtGui

from rofl_toolbox.generic_python.pyside2_generic import Pyside2Generic

from rofl_toolbox.data_base_system.constants import CACHES, FLIPBOOKS, RENDERS, WEDGES
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import Label, ActionButtons, CheckBox, MessageBox
from rofl_toolbox.file_manager.widgets.increment.api.increment_houdini import IncrementHoudini
from rofl_toolbox.file_manager.constants import MSG

class IncrementHoudiniUi(QtWidgets.QDialog):
    def __init__(self, scene_sid=None, sid=None):
        super(IncrementHoudiniUi, self).__init__()
        self.incr_api = IncrementHoudini(scene_sid=scene_sid, sid=sid)
        self.files_to_copy = False
        self.setWindowTitle("Increment Scene")
        self.setup_ui()
        self._init_ui()
        self.resize(1000, 650)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "../resources/icons/rofl_logo.png")))
        self.show()

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_main.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.modify_layout()
        self.add_widgets_to_layouts()
        self.setup_connections()
        Pyside2Generic().center_on_screen(self)

    def create_widgets(self):
        # BTN
        self.btn_increment = ActionButtons("Increment Scene")
        self.btn_release = ActionButtons("Increment And Release Scene")
        self.btn_save_work = ActionButtons("Just Save Work (With Commentaries)")
        # LABELS
        self.lbl_cache_export = Label("Export Files")
        self.lbl_commentaries = Label("Commentaries")
        self.lbl_incr_enable = QtWidgets.QLabel("Is Reading Increment")
        self.lbl_infos = QtWidgets.QLabel("States : ")
        self.lbl_pictures_export = Label("Export Pictures")
        self.lbl_read_version = QtWidgets.QLabel("Is Reading Work")
        self.lbl_release_enable = QtWidgets.QLabel("is Reading Release")
        # COMBO BOX
        self.cb_cache = CheckBox("Caches")
        self.cb_cache_select = CheckBox("Select All")
        self.cb_flipbook = CheckBox("Flipbook")
        self.cb_flipbook_select = CheckBox("Select All")
        self.cb_render = CheckBox("Render")
        self.cb_render_select = CheckBox("Select All")
        self.cb_wedges = CheckBox("Wedges")
        self.cb_wedges_select = CheckBox("Select All")
        # LIST WIDGETS
        self.lw_cache = QtWidgets.QListWidget()
        self.lw_flipbook = QtWidgets.QListWidget()
        self.lw_render = QtWidgets.QListWidget()
        self.lw_wedges = QtWidgets.QListWidget()
        # TEXT EDIT
        self.te_commentaries = QtWidgets.QTextEdit()

    def modify_widgets(self):
        # BTN
        self.btn_increment.setFixedHeight(30)
        self.btn_release.setFixedHeight(30)
        self.btn_save_work.setFixedHeight(30)
        # LABELS
        self.lbl_incr_enable.setObjectName("IsMaybeValid")
        self.lbl_read_version.setObjectName("IsValid")
        self.lbl_release_enable.setObjectName('IsNotValid')
        # LIST WIDGET
        self.lw_cache.setMinimumSize(QtCore.QSize(260, 20))
        self.lw_cache.setSortingEnabled(True)
        self.lw_cache.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.lw_flipbook.setSortingEnabled(True)
        self.lw_flipbook.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.lw_render.setSortingEnabled(True)
        self.lw_render.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)
        self.lw_wedges.setSortingEnabled(True)
        self.lw_wedges.setSelectionMode(QtWidgets.QAbstractItemView.NoSelection)

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)

        self.btn_layout = QtWidgets.QHBoxLayout()
        self.elements_layout = QtWidgets.QHBoxLayout()
        self.flipbook_layout = QtWidgets.QVBoxLayout()
        self.header_layout = QtWidgets.QHBoxLayout()
        self.leftV_layout = QtWidgets.QVBoxLayout()
        self.pictures_layout = QtWidgets.QHBoxLayout()
        self.render_layout = QtWidgets.QVBoxLayout()
        self.rightV_layout = QtWidgets.QVBoxLayout()
        self.wedges_layout = QtWidgets.QVBoxLayout()

    def modify_layout(self):
        self.leftV_layout.setContentsMargins(0, 0, 5, 0)

    def add_widgets_to_layouts(self):
        # COLUMN CACHES
        self.leftV_layout.addWidget(self.lbl_cache_export)
        self.leftV_layout.addWidget(self.cb_cache)
        self.leftV_layout.addWidget(self.lw_cache)
        self.leftV_layout.addWidget(self.cb_cache_select)
        # COLUMN FLIPBOOK
        self.flipbook_layout.addWidget(self.cb_flipbook)
        self.flipbook_layout.addWidget(self.lw_flipbook)
        self.flipbook_layout.addWidget(self.cb_flipbook_select)
        # COLUMN RENDERS
        self.render_layout.addWidget(self.cb_render)
        self.render_layout.addWidget(self.lw_render)
        self.render_layout.addWidget(self.cb_render_select)
        # COLUMN WEDGES
        self.wedges_layout.addWidget(self.cb_wedges)
        self.wedges_layout.addWidget(self.lw_wedges)
        self.wedges_layout.addWidget(self.cb_wedges_select)
        # HEADER PICTURES
        self.pictures_layout.addLayout(self.flipbook_layout)
        self.pictures_layout.addLayout(self.wedges_layout)
        self.pictures_layout.addLayout(self.render_layout)
        # BUTTONS BOX
        self.btn_layout.addWidget(self.btn_save_work)
        self.btn_layout.addWidget(self.btn_increment)
        self.btn_layout.addWidget(self.btn_release)
        # RIGHT BOX
        self.rightV_layout.addWidget(self.lbl_pictures_export)
        self.rightV_layout.addLayout(self.pictures_layout)
        self.rightV_layout.addWidget(self.lbl_commentaries)
        self.rightV_layout.addWidget(self.te_commentaries)
        self.rightV_layout.addLayout(self.btn_layout)
        # HEADER LEGENDS
        self.header_layout.addWidget(self.lbl_infos)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.lbl_read_version)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.lbl_incr_enable)
        self.header_layout.addStretch(1)
        self.header_layout.addWidget(self.lbl_release_enable)
        self.header_layout.addStretch(30)
        # GLOBAL BOX
        self.elements_layout.addLayout(self.leftV_layout)
        self.elements_layout.addLayout(self.rightV_layout)
        # MAIN BOX
        self.main_layout.addLayout(self.header_layout)
        self.main_layout.addLayout(self.elements_layout)

    def setup_connections(self):
        # BTN
        self.btn_increment.clicked.connect(self.increment_scene)
        self.btn_release.clicked.connect(self.release_scene)
        self.btn_save_work.clicked.connect(self.just_save_work)
        # COMBO BOX
        self.cb_cache.clicked.connect(self.get_caches)
        self.cb_cache_select.clicked.connect(self.select_all_caches)
        self.cb_flipbook.clicked.connect(self.get_flipbooks)
        self.cb_flipbook_select.clicked.connect(self.select_all_flipbooks)
        self.cb_render.clicked.connect(self.get_renders)
        self.cb_render_select.clicked.connect(self.select_all_renders)
        self.cb_wedges.clicked.connect(self.get_wedgers)
        self.cb_wedges_select.clicked.connect(self.select_all_wedges)

    def _check_commentaries(self):
        """
        check if the user has filled the commentaries
        Returns: True if succeed

        """
        self.commentary = self.te_commentaries.toPlainText()
        if not self.commentary:
            msg = MSG["ENTER_COMMENTARY"]
            msg_box = MessageBox(message=msg, warning=True)
            msg_box.show()
            msg_box.exec_()
            if not msg_box.valid:
                return False, ""
        return True

    def _init_ui(self):
        """
        init UI at start

        """
        self.cb_cache.setChecked(True)
        self.get_caches()
        self.cb_flipbook.setChecked(True)
        self.get_flipbooks()
        self.cb_render.setChecked(True)
        self.get_renders()
        self.cb_wedges.setChecked(True)
        self.get_wedgers()

    def add_node_to_listwidget(self, list_widget, node, icon):
        """
        Generic code to set the list widget items
        Args:
            list_widget: which list to add item
            node: the name of the item
            icon: the icon to set on the item

        """
        lw_item = QtWidgets.QListWidgetItem(node.node_name)
        lw_item.node = node
        lw_item.setCheckState(QtCore.Qt.Unchecked)
        lw_item.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable)
        lw_item.setIcon(QtGui.QIcon(icon))
        if node.read_version.evalAsString() == "000":
            lw_item.setTextColor(QtGui.QColor("#5BE79B"))
        else:
            lw_item.setTextColor(QtGui.QColor("#E7C95B"))

        if node.search_release.eval():
            lw_item.setTextColor(QtGui.QColor("#E7705B"))
        list_widget.addItem(lw_item)

    def get_caches(self):
        """
        collect all the rofl caches and caches layers in the current scene

        """
        if not self.cb_cache.isChecked():
            self.lw_cache.clear()
            self.cb_cache_select.setChecked(False)
            self.cb_cache_select.setEnabled(False)
            return False
        self.cb_cache_select.setEnabled(True)

        # GET ICONS
        bgeo_icon = hou.ui.createQtIcon(hou.nodeType("Object/geo").icon())
        vdb_icon = hou.ui.createQtIcon(hou.nodeType("Sop/vdb").icon())
        abc_icon = hou.ui.createQtIcon(hou.nodeType("Sop/alembic").icon())
        # GET ALL FILECACHES
        rofl_caches = self.incr_api.get_caches()
        # BUILD LISTS
        bgeo_caches = [i for i in rofl_caches if i.geo_type.evalAsString() == "bgeo"]
        vdb_caches = [i for i in rofl_caches if i.geo_type.evalAsString() == "vdb"]
        abc_caches = [i for i in rofl_caches if i.geo_type.evalAsString() == "abc"]

        for node in bgeo_caches:
            self.add_node_to_listwidget(list_widget=self.lw_cache, node=node, icon=bgeo_icon)
        for node in vdb_caches:
            self.add_node_to_listwidget(list_widget=self.lw_cache, node=node, icon=vdb_icon)
        for node in abc_caches:
            self.add_node_to_listwidget(list_widget=self.lw_cache, node=node, icon=abc_icon)
        return True

    def get_flipbooks(self):
        """
        collect all the rofl flipbooks in the current scene

        """
        if not self.cb_flipbook.isChecked():
            self.lw_flipbook.clear()
            self.cb_flipbook_select.setChecked(False)
            self.cb_flipbook_select.setEnabled(False)
            return False
        self.cb_flipbook_select.setEnabled(True)

        # GET ICON
        folder_icon = os.path.join(hou.hscriptExpression("$ROFL_TOOLS"), "resources/icons/folderV.png")
        # GET ALL FLIPBOOKS
        rofl_flipbooks = self.incr_api.get_flipbooks()
        # ADD LIST TO LISTWIDGET
        for node in rofl_flipbooks:
            self.add_node_to_listwidget(list_widget=self.lw_flipbook, node=node, icon=folder_icon)

    def get_renders(self):
        """
        collect all the rofl renders in the current scene

        """
        if not self.cb_render.isChecked():
            self.lw_render.clear()
            self.cb_render_select.setChecked(False)
            self.cb_render_select.setEnabled(False)
            return False
        self.cb_render_select.setEnabled(True)

        # GET ICON
        folder_icon = os.path.join(hou.hscriptExpression("$ROFL_TOOLS"), "resources/icons/folderV.png")
        # GET ALL RENDERS
        rofl_renders = self.incr_api.get_renders()
        # ADD LIST TO LISTWIDGET
        for node in rofl_renders:
            self.add_node_to_listwidget(list_widget=self.lw_render, node=node, icon=folder_icon)

    def get_wedgers(self):
        """
        collect all the rofl wedgers in the current scene

        """
        if not self.cb_wedges.isChecked():
            self.lw_wedges.clear()
            return False

        # GET ICON
        folder_icon = os.path.join(hou.hscriptExpression("$ROFL_TOOLS"), "resources/icons/folderV.png")
        # GET ALL WEDGES
        wedgers = self.incr_api.get_wedgers()
        # ADD LIST TO LISTWIDGET
        for node in wedgers:
            self.add_node_to_listwidget(list_widget=self.lw_wedges, node=node, icon=folder_icon)

    def _get_datas(self):
        """
        get all the selected user datas
        Returns: selected user datas

        """
        if not self._check_commentaries():
            return False

        caches = [self.lw_cache.item(i).node for i in range(self.lw_cache.count())
                  if self.lw_cache.item(i).checkState()]
        flipbooks = [self.lw_flipbook.item(i).node for i in range(self.lw_flipbook.count())
                     if self.lw_flipbook.item(i).checkState()]
        renders = [self.lw_render.item(i).node for i in range(self.lw_render.count())
                   if self.lw_render.item(i).checkState()]
        wedges = [self.lw_wedges.item(i).node for i in range(self.lw_wedges.count())
                  if self.lw_wedges.item(i).checkState()]

        datas = {}
        datas.update({CACHES: caches})
        datas.update({FLIPBOOKS: flipbooks})
        datas.update({RENDERS: renders})
        datas.update({WEDGES: wedges})

        return datas

    def increment_scene(self):
        """
        launch increment action
        Returns: True if success

        """
        datas = self._get_datas()
        if not datas:
            return False, ""

        success, log = self.incr_api.increment_scene(commentary=self.commentary, datas=datas)
        self.close()
        self.files_to_copy = True if self.incr_api.files_to_copy else False
        return success, log

    def just_save_work(self):
        """
        just a ctrl+s with modified commentaries
        Returns: True if succeed

        """
        if not self._check_commentaries():
            return False, ""

        success, log = self.incr_api.just_save_work(commentary=self.commentary)
        self.close()
        self.files_to_copy = False
        return success, log

    def release_scene(self):
        """
        launch release action
        Returns: True if success

        """
        datas = self._get_datas()
        if not datas:
            return False, ""

        success, log = self.incr_api.release_scene(commentary=self.commentary, datas=datas)
        self.close()
        self.files_to_copy = True if self.incr_api.files_to_copy else False
        return success, log

    def select_all_caches(self):
        """
        select all caches at once

        """
        cache_count = self.lw_cache.count()
        for i in range(cache_count):
            if self.cb_cache_select.isChecked():
                self.lw_cache.item(i).setCheckState(QtCore.Qt.Checked)
            else:
                self.lw_cache.item(i).setCheckState(QtCore.Qt.Unchecked)

    def select_all_flipbooks(self):
        """
        select all flipbooks at once

        """
        flipbook_count = self.lw_flipbook.count()
        for i in range(flipbook_count):
            if self.cb_flipbook_select.isChecked():
                self.lw_flipbook.item(i).setCheckState(QtCore.Qt.Checked)
            else:
                self.lw_flipbook.item(i).setCheckState(QtCore.Qt.Unchecked)

    def select_all_renders(self):
        """
        select all renders at once

        """
        render_count = self.lw_render.count()
        for i in range(render_count):
            if self.cb_render_select.isChecked():
                self.lw_render.item(i).setCheckState(QtCore.Qt.Checked)
            else:
                self.lw_render.item(i).setCheckState(QtCore.Qt.Unchecked)

    def select_all_wedges(self):
        """
        select all wedges at once

        """
        wedge_count = self.lw_wedges.count()
        for i in range(wedge_count):
            if self.cb_wedges_select.isChecked():
                self.lw_wedges.item(i).setCheckState(QtCore.Qt.Checked)
            else:
                self.lw_wedges.item(i).setCheckState(QtCore.Qt.Unchecked)

    def closeEvent(self, event):
        """
        exec on close window event

        """
        self.files_to_copy = False

if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    fenetre = IncrementHoudiniUi()
    fenetre.show()
    app.exec_()