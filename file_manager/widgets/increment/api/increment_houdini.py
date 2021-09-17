import shutil
import os

import hou

from rofl_toolbox.generic_python.softs_generic.generic_houdini.general import HouGeneral
from rofl_toolbox.data_base_system.sid_scene_manager_common import SidSceneManagerCommon
from rofl_toolbox.file_manager.widgets.file_copyer.api.file_copyer import FileCopyer
from rofl_toolbox.data_base_system.constants import CACHES, FLIPBOOKS, RENDERS, WEDGES

from rofl_pipeline_tools.rofl_filecache import FileCache
from rofl_pipeline_tools.rofl_filecache_layer import FileCacheLayer
from rofl_pipeline_tools.rofl_flipbook import Flipbook
from rofl_pipeline_tools.rofl_render import Render
from rofl_pipeline_tools.rofl_wedger import Wedger
from rofl_pipeline_tools.rofl_daillies import Daillies
from rofl_pipeline_tools.constants import ROFL_CACHE, ROFL_CACHE_LAYER, ROFL_FLIPBOOK,\
                                          ROFL_RENDER, ROFL_WEDGER, ROFL_DAILLIES


class IncrementHoudini:
    def __init__(self, scene_sid, sid):
        self.files_to_copy = False
        self.scene_sid = scene_sid
        self.houGeneral = HouGeneral()
        self.sidActions = SidSceneManagerCommon(sid=sid)
        self.extension = self.houGeneral.get_license_category()

    def _add_file_in_sid_bdd(self, datas=None, release=False):
        """
        add files element in the data base
        Args:
            datas: the datas from UI
            release: tell if release or not

        """
        if not datas:
            return False

        files = {}
        self.sidActions.add_files_prepare_caches(datas, files, release, self.incr_sid)
        self.sidActions.add_files_prepare_flipbooks(datas, files, release, self.incr_sid)
        self.sidActions.add_files_prepare_renders(datas, files, release, self.incr_sid)
        self.sidActions.add_files_prepare_wedges(datas, files, release, self.incr_sid)
        self.sidActions.add_files(files)

    def _get_save_path(self, incr=False, commentary="tmp_work"):
        """
        get the scene paths with the database help
        Args:
            incr: is it an increment
            commentary: commentary attach to the save

        Returns: the save scene path

        """
        path, log = self.sidActions.incr_save(scene_SID=self.scene_sid, incr=incr, software="Houdini", commentary=commentary)
        if isinstance(path, bool):
            return False, log

        return path, ""

    def _get_save_path_release(self, incr=False, commentary="tmp_work"):
        """
        get the scene paths with the database help
        Args:
            incr: is it an increment
            commentary: commentary attach to the save

        Returns: the save scene path

        """
        path, log = self.sidActions.release_save(incr=incr, software="Houdini", commentary=commentary)
        if isinstance(path, bool):
            return False, log

        return path, ""

    def _prepare_FileCopyer(self, files, category, name):
        """
        prepare in detail the FileCopyer database
        Args:
            files: files datas provide from the rofl_hda
            category: the type of the files
            name: the node name

        """
        for file, paths in files.items():
            scene = SidSceneManagerCommon(self.scene_sid).sid_replace_version("000")
            src = paths["src"]
            tgt = paths["tgt"]
            self.SID_FC.build_data_files(scene=scene, category=category, group=name, filename=file, src=src, tgt=tgt)

    def _prepare_copy_files(self, datas=None, release=False):
        """
        prepare FileCopyer database to launch the copy after saving process
        Args:
            datas: the datas from the UI
            release: tell if release or not

        """
        if not datas:
            return False

        self.SID_FC = FileCopyer()
        for item in datas[CACHES]:
            files = item.get_copy_files_infos(sid_src_version=self.scene_sid, sid_tgt_version=self.incr_sid, release=release)
            self._prepare_FileCopyer(files=files, category=CACHES, name=item.node_name)

        for item in datas[FLIPBOOKS]:
            files = item.get_copy_files_infos(sid_src_version=self.scene_sid, sid_tgt_version=self.incr_sid, release=release)
            self._prepare_FileCopyer(files=files, category=FLIPBOOKS, name=item.node_name)

        for item in datas[RENDERS]:
            files = item.get_copy_files_infos(sid_src_version=self.scene_sid, sid_tgt_version=self.incr_sid, release=release)
            self._prepare_FileCopyer(files=files, category=RENDERS, name=item.node_name)

        for item in datas[WEDGES]:
            if item.node_type_name == ROFL_WEDGER:
                files = item.get_copy_files_infos(sid_src_version=self.scene_sid, sid_tgt_version=self.incr_sid, release=release)
                self._prepare_FileCopyer(files=files, category=WEDGES, name=item.node_name)

            if item.node_type_name == ROFL_DAILLIES:
                nodes = item.get_copy_files_infos(sid_src_version=self.scene_sid, sid_tgt_version=self.incr_sid, release=release)
                for node, files in nodes.items():
                    self._prepare_FileCopyer(files=files, category=WEDGES, name=node)

        self.SID_FC.save_json()
        self.files_to_copy = True if self.SID_FC.datas else False

    def _save_scene(self, path=None, only_save=False):
        """
        save work path
        Args:
            path: the work path
            only_save: tell if we just save, or if it is an increment

        """
        if not only_save:
            self.houGeneral.set_env("SID", self.sidActions.SID)

        path += "." + self.extension
        hou.hipFile.save(file_name=path, save_to_recent_files=True)
        return path

    def _save_copy_incr(self, path=None):
        """
        define increment path and copy work scene to it
        Args:
            path: the work path

        """
        incr_path = self.sidActions.SID_complete_scene_path()
        incr_path += "." + self.extension
        shutil.copy(path, incr_path)

    def _save_copy_release(self, path=None):
        """
        define release path and copy work scene to it
        Args:
            path: the work path

        """
        release_path = self.sidActions.SID_release_complete_scene_path()
        release_path += "." + self.extension
        release_folder = os.path.dirname(release_path)
        if not os.path.exists(release_folder):
            os.makedirs(release_folder)
        shutil.copy(path, release_path)

    def get_caches(self):
        """
        collect all rofl_cache and rofl_cache_layer
        Returns: the cache founds

        """
        rofl_caches = [FileCache(i) for i in hou.nodeType("Sop/{0}".format(ROFL_CACHE)).instances()]
        rofl_caches += [FileCacheLayer(i) for i in hou.nodeType("Sop/{0}".format(ROFL_CACHE_LAYER)).instances()]
        rofl_caches = [i for i in rofl_caches if not i.override_output.eval()]
        return rofl_caches

    def get_flipbooks(self):
        """
        collect all rofl_flipbooks
        Returns: the flipbooks founds

        """
        rofl_flipbooks = [Flipbook(i) for i in hou.nodeType("Top/{0}".format(ROFL_FLIPBOOK)).instances()]
        rofl_flipbooks = [i for i in rofl_flipbooks if i.node.parent().type() != hou.nodeType("Top/{0}".format(ROFL_WEDGER))]
        rofl_flipbooks = [i for i in rofl_flipbooks if not i.override_output.eval()]
        rofl_flipbooks = [i for i in rofl_flipbooks if not i.override_mp4.eval()]
        return rofl_flipbooks

    def get_renders(self):
        """
        collect all rofl_renders
        Returns: the renders founds

        """
        rofl_renders = [Render(i) for i in hou.nodeType("Top/{0}".format(ROFL_RENDER)).instances()]
        rofl_renders = [i for i in rofl_renders if not i.override_output.eval()]
        return rofl_renders

    def get_wedgers(self):
        """
        collect all rofl_wedgers and rofl_daillies
        Returns: the wedges founds

        """
        # GET ALL WEDGES
        # rofl_wedgers = [Wedger(i) for i in hou.nodeType("Top/rofl_wedger").instances()]
        # rofl_wedgers = [i for i in rofl_wedgers if i.node.parent().name() != "wedgers"]
        # rofl_wedgers = [i for i in rofl_wedgers if not i.override_scene.eval()]
        # GET ALL DAILLIES
        rofl_daillies = [Daillies(i) for i in hou.nodeType("Top/{0}".format(ROFL_DAILLIES)).instances()]
        rofl_daillies = [i for i in rofl_daillies if not i.override_output.eval()]
        rofl_daillies = [i for i in rofl_daillies if not i.override_mp4.eval()]
        # MERGE THE TWO LISTS
        # wedgers = rofl_wedgers + rofl_daillies
        return rofl_daillies

    def just_save_work(self, commentary):
        """
        action link the just save work button of the Incrementer
        """
        # get work scene path
        path, log = self._get_save_path(commentary=commentary)
        if not path:
            return False, log

        # don't apply new sid scene (only on self increment)
        if self.sidActions.check_matched_SID(self.scene_sid):
            self.houGeneral.set_env("SID", self.sidActions.SID)

        # save scene
        self._save_scene(path=path, only_save=True)
        self.files_to_copy = False
        return True, ""

    def increment_scene(self, commentary, datas=None):
        """
        action link the increment button of the Incrementer
        """
        # get work scene path
        path, log = self._get_save_path(incr=True, commentary=commentary)
        if not path:
            self.files_to_copy = False
            return False, log

        if not self.sidActions.check_matched_SID(self.scene_sid):
            self.sidActions.SID = self.sidActions.sid_replace_version("000")

        # INCREMENT FILES
        self.incr_sid = self.sidActions.SID
        self._add_file_in_sid_bdd(datas=datas)
        self._prepare_copy_files(datas=datas)
        # SAVE SCENES
        path = self._save_scene(path=path)
        if self.sidActions.check_matched_SID(self.scene_sid):
            self._save_copy_incr(path=path)

        return True, ""

    def release_scene(self, commentary, datas=None):
        """
        action link the increment button of the Incrementer
        """
        # get work scene path
        path, log = self._get_save_path_release(incr=True, commentary=commentary)
        if not path:
            self.files_to_copy = False
            return False, log

        # INCREMENT FILES
        self.incr_sid = self.sidActions.SID
        self._add_file_in_sid_bdd(datas=datas, release=True)
        self._prepare_copy_files(datas=datas, release=True)
        # SAVE SCENES
        path = self._save_scene(path=path)
        self._save_copy_incr(path=path)
        self._save_copy_release(path=path)

        return True, ""