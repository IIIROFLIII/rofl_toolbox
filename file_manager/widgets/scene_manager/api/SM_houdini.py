import os

import hou

from rofl_toolbox.file_manager.widgets.settings.api.settings import Settings

from rofl_toolbox.data_base_system.sid_scene_manager_common import SidSceneManagerCommon

from rofl_toolbox.generic_python.softs_generic.generic_houdini.general import HouGeneral
from rofl_pipeline_tools.rofl_node_color import NodeColor
from rofl_toolbox.file_manager.widgets.increment.ui.increment_houdini_ui import IncrementHoudiniUi

from rofl_pipeline_tools.rofl_filecache import FileCache
from rofl_pipeline_tools.rofl_filecache_layer import FileCacheLayer
from rofl_pipeline_tools.rofl_flipbook import Flipbook
from rofl_pipeline_tools.rofl_render import Render
from rofl_pipeline_tools.rofl_wedger import Wedger
from rofl_pipeline_tools.rofl_daillies import Daillies
from rofl_pipeline_tools.constants import ROFL_CACHE, ROFL_CACHE_LAYER, ROFL_WEDGER, ROFL_DAILLIES

class SceneManagerHoudini:
    def __init__(self, sid=None):
        self.software = "Houdini"
        self.files_to_copy = False
        self.houGeneral = HouGeneral()
        self.sidActions = SidSceneManagerCommon(sid=sid)
        self.extension = self.houGeneral.get_license_category()

    def _setup_caches(self, scene="", release=False):
        """
        set all incremented caches on the selected version
        Args:
            scene: the scene SID
            release: release state

        """
        datas = self.sidActions.get_all_scene_caches(scene=scene, release=release)
        version = self.sidActions.SID_version

        for node_name in datas:
            node_path = self.sidActions.get_scene_cache_node_path(scene=scene, release=release, node=node_name)
            node = hou.node(node_path)
            if node.type().name() == ROFL_CACHE:
                cache_node = FileCache(node)
                if release:
                    cache_node.search_release.set(1)
                cache_node.read_version.set(version)
            elif node.type().name() == ROFL_CACHE_LAYER:
                cache_node = FileCacheLayer(node)
                if release:
                    cache_node.search_release.set(1)
                cache_node.read_version.set(version)

    def _setup_flipbooks(self, scene="", release=False):
        """
        set all incremented flipbooks on the selected version
        Args:
            scene: the scene SID
            release: release state

        """
        datas = self.sidActions.get_all_scene_flipbooks(scene=scene, release=release)
        version = self.sidActions.SID_version

        for node_name in datas:
            node_path = self.sidActions.get_scene_flipbook_node_path(scene=scene, release=release, node=node_name)
            node = hou.node(node_path)
            flipbook_node = Flipbook(node)
            if release:
                flipbook_node.search_release.set(1)
            flipbook_node.read_version.set(version)

    def _setup_renders(self, scene="", release=False):
        """
        set all incremented renders on the selected version
        Args:
            scene: the scene SID
            release: release state

        """
        datas = self.sidActions.get_all_scene_renders(scene=scene, release=release)
        version = self.sidActions.SID_version

        for node_name in datas:
            node_path = self.sidActions.get_scene_render_node_path(scene=scene, release=release, node=node_name)
            node = hou.node(node_path)
            render_node = Render(node)
            if release:
                render_node.search_release.set(1)
            render_node.read_version.set(version)

    def _setup_wedges(self, scene="", release=False):
        """
        set all incremented wedges on the selected version
        Args:
            scene: the scene SID
            release: release state

        """
        datas = self.sidActions.get_all_scene_wedges(scene=scene, release=release)
        version = self.sidActions.SID_version

        for node_name in datas:
            node_path = self.sidActions.get_scene_wedge_node_path(scene=scene, release=release, node=node_name)
            node = hou.node(node_path)
            if node.type().name() == ROFL_WEDGER:
                wedger_node = Wedger(node)
                if release:
                    wedger_node.search_release.set(1)
                wedger_node.read_version.set(version)
            elif node.type().name() == ROFL_DAILLIES:
                daillies_node = Daillies(node)
                if release:
                    daillies_node.search_release.set(1)
                daillies_node.read_version.set(version)

    def import_cache(self, file_sequence):
        """
        improt given file in SOP
        Args:
            file_sequence: the files to import (it must be a list)

        """
        # get file infos
        self.sidActions.SID = self.sidActions.conform_file_for_sid(file=os.path.basename(file_sequence[0]))
        file_name = self.sidActions.SID_filename
        file_extension = os.path.splitext(file_sequence[0])[-1]

        # create top node at object level
        top_level = hou.node("/obj/")
        geo_node = top_level.createNode("geo", file_name)
        geo_node.move([-4, 0])
        geo_node.setColor(hou.Color(NodeColor().import_geo))
        merge_node = geo_node.createNode("merge")
        merge_node.move([0, -2])

        for i, file in enumerate(file_sequence):
            # create file node
            if "abc" in file_extension:
                file_node = geo_node.createNode("alembic", "IN_{0}".format(file_name))
                file_node.parm("fileName").set(file)
            else:
                file_node = geo_node.createNode("file", "IN_{0}".format(file_name))
                file_node.parm("file").set(file)
            file_node.setColor(hou.Color(NodeColor().input))
            file_node.move([i*4, 0])
            merge_node.setNextInput(file_node)

        # create null node
        null_node = geo_node.createNode("null", "OUT_{0}".format(file_name))
        null_node.setNextInput(merge_node)
        null_node.move([0, -4])
        null_node.setColor(hou.Color(NodeColor().null))
        null_node.setDisplayFlag(True)
        null_node.setRenderFlag(True)
        geo_node.setCurrent(True, clear_all_selected=True)

    def import_picture(self, file_sequence):
        """
        improt given file in COP
        Args:
            file_sequence: the files to import

        """
        self.sidActions.SID = self.sidActions.conform_file_for_sid(file=os.path.basename(file_sequence))
        file_name = self.sidActions.SID_filename

        # create top node at object level
        top_level = hou.node("/obj/")
        cop_node = hou.node(top_level.path() + "/imported_pictures")
        if not cop_node:
            cop_node = top_level.createNode("cop2net", "imported_pictures")
            cop_node.move([-4, 0])
            cop_node.setColor(hou.Color(NodeColor().import_geo))

        # create file node
        if file_name.isdigit():
            file_name = "file_{0}".format(file_name)
        file_node = cop_node.createNode("file", file_name)
        file_node.parm("filename1").set(file_sequence)
        file_node.setColor(hou.Color(NodeColor().input))
        file_node.setDisplayFlag(True)
        file_node.setRenderFlag(True)
        file_node.setCurrent(True, clear_all_selected=True)

    def launch_player(self, file_sequence):
        HouGeneral().load_in_mplay(path=file_sequence)

    def save(self):
        """
        action link to the save button of the FM
        """
        # set SID variable
        scene_SID = hou.getenv('SID')
        # get save path and add scene in bdd
        self.sidActions.SID = self.sidActions.sid_replace_version("000")
        path, log = self.sidActions.save(scene_SID=scene_SID, software="Houdini")

        # case where the current scene is not a pipe scene
        if not scene_SID:
            if isinstance(path, bool):
                return False, log
            # classic save
            self.houGeneral.set_env("SID", self.sidActions.SID)
            hou.setFps(Settings().get_fps())
            hou.playbar.setRealTime(True)
            path += "." + self.extension
            hou.hipFile.save(file_name=path, save_to_recent_files=True)
            self.files_to_copy = False
            return True, ""
        # case where the scene is a pipe scene
        else:
            if isinstance(path, bool) and path:
                # load increment ui
                incr = IncrementHoudiniUi(scene_sid=scene_SID, sid=self.sidActions.SID)
                incr.exec_()
                self.files_to_copy = incr.files_to_copy
                return True, ""
            return False, log

    def open(self, release=False):
        """
        action link to the open button of the FM
        """
        # get file path
        path = self.sidActions.SID_complete_scene_path()
        path += "." + self.extension
        # load scene
        hou.hipFile.load(path, ignore_load_warnings=True)
        # set hda parameters according to the files database
        self._setup_caches(scene=self.sidActions.SID, release=release)
        self._setup_flipbooks(scene=self.sidActions.SID, release=release)
        self._setup_renders(scene=self.sidActions.SID, release=release)
        self._setup_wedges(scene=self.sidActions.SID, release=release)
        # set scene path on work scene
        self.sidActions.SID = self.sidActions.sid_replace_version("000")
        work_path = self.sidActions.SID_complete_scene_path()
        work_path += "." + self.extension
        hou.hipFile.setName(work_path)
        return True, ""

