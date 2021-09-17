import os
import shutil

import hou

from rofl_toolbox.data_base_system.constants import SID_FILE_SEPARATOR

from rofl_pipeline_tools.rofl_flipbook import Flipbook
from rofl_pipeline_tools.rofl_wedger import Wedger
from rofl_pipeline_tools.constants import ROFL_WEDGER

class Daillies(Flipbook):
    def __init__(self, node):
        Flipbook.__init__(self, node)

    @property
    def index(self):
        return self.node.parm("index")

    @property
    def session(self):
        return self.node.parm("session")

    def _rename_files_sequence(self, folder):
        """
        rename generated files when node is rename in houdini
        Args:
            folder: the name of the folder which contain the files
        """
        if not os.path.exists(folder):
            return False

        for i in os.listdir(folder):
            if len(i.split(SID_FILE_SEPARATOR)) != 6:
                continue

            self.bdd.SID = self.bdd.conform_file_for_sid(i)
            self.bdd.SID = self.bdd.sid_replace_filename(self.node_name)

            new_file = self.bdd.SID_complete_daillies_path(session=self.session.eval())
            os.rename(os.path.join(folder, i), new_file)

    def _rename_files_mp4(self, folder):
        """
        rename generated files when node is rename in houdini
        Args:
            folder: the name of the folder which contain the files
        """
        if not os.path.exists(folder):
            return False

        for i in os.listdir(folder):
            if len(i.split(SID_FILE_SEPARATOR)) != 6:
                continue

            self.bdd.SID = self.bdd.conform_file_for_sid(i)
            self.bdd.SID = self.bdd.sid_replace_filename(self.node_name)

            new_file = self.bdd.SID_complete_daillies_mp4_path(session=self.session.eval())
            os.rename(os.path.join(folder, i), new_file)

    def build_daillies_SID(self, script_padding=False, force_sid=None):
        """
        build proper data_base_system according to the flipbook node
        """
        frame = self.find_frame(script_padding=script_padding)

        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString()) if not force_sid else force_sid
        self.bdd.SID = self.bdd.build_SID_file(name=self.session.eval(), wedge_suffix=self.index.eval(), frame=frame)

    def clean_scene(self):
        wedger_container = hou.node(self.node_path + '/wedgers')
        wedgers = [i for i in hou.nodeType('Top/{0}'.format(ROFL_WEDGER)).instances() if i.parent() == wedger_container]
        wedger = Wedger(wedgers[-1])
        wedger.link_parameters(clean=True)
        wedger.activate_cache_wedges(clean=True)

    def find_version_files(self):
        """
        list all cache version available in increment sections
        Returns: a liste for houdini menu
        """
        ####
        # la on recupere les versions de scenes faudrait mieux recuperer les versions quand le cache existe
        # a voir quand les caches ajouteront dans la bdd les elements
        ####
        if self.override_output.eval():
            return ["---", "---"]

        self.menu_item.set('')
        search_release = self.search_release.eval()
        versions_list = self.bdd.get_incr_wedgers_version_list(self, release=search_release)
        for i in versions_list:
            self.menu_item.set("{0} {1}".format(self.menu_item.eval(), i))

        # BUILD MENU FOR "MENU SCRIPT WORKING"
        menuitems = self.menu_item.eval().split()
        menu = ["000", "000"]
        for item in menuitems:
            menu.append(item)
            menu.append(item)

        return menu

    def get_copy_files_infos(self, sid_src_version=None, sid_tgt_version=None, release=False):
        files = {}

        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_name(self.node_name)
        if not self.search_release.eval():
            folder = self.bdd.SID_daillies_folder(self.session.evalAsString())
        else:
            folder = self.bdd.SID_release_daillies_folder(self.session.evalAsString())
        if not os.path.isdir(folder):
            return files

        file_sources = self.get_source_files(folder=folder)
        files[self.node_name] = {}
        for file in file_sources:
            filename = os.path.basename(file)
            self.bdd.SID = self.bdd.conform_file_for_sid(filename)
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)

            if not release:
                tgt = self.bdd.SID_complete_daillies_path(session=self.session.eval())
            else:
                tgt = self.bdd.SID_release_complete_daillies_path(session=self.session.eval())
            files[self.node_name].update({filename: {"src": file, "tgt": tgt}})

        # GET MP4
        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_name(self.node_name)
        if not self.search_release.eval():
            folder = self.bdd.SID_daillies_folder_mp4(self.session.evalAsString())
        else:
            folder = self.bdd.SID_release_daillies_folder_mp4(self.session.evalAsString())
        if not os.path.isdir(folder):
            return files

        mp4_sources = self.get_source_files_mp4(folder=folder)
        for file in mp4_sources:
            filename = os.path.basename(file)
            self.bdd.SID = self.bdd.conform_file_for_sid(filename)
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)

            if not release:
                tgt = self.bdd.SID_complete_daillies_mp4_path(session=self.session.eval())
            else:
                tgt = self.bdd.SID_release_complete_daillies_mp4_path(session=self.session.eval())
            files[self.node_name].update({filename: {"src": file, "tgt": tgt}})

        # GET WEDGERS
        wedgers = [i for i in hou.nodeType("Top/{0}".format(ROFL_WEDGER)).instances() if i.parent().parent().name() == self.node_name]
        for wedger in wedgers:
            wedge_item = Wedger(wedger)
            files["{0}_{1}".format(self.node_name, wedge_item.wedge_suffix.eval())] = wedge_item.get_copy_files_infos(sid_src_version, sid_tgt_version, release=release)

        return files

    def get_source_files_mp4(self, folder=None):
        files = os.listdir(folder)
        sid_list = self.bdd.conform_sid_to_list()
        sources = [os.path.join(folder, file).replace("\\", "/") for file in files if all(item in self.bdd.conform_file_to_list(file) for item in sid_list)]

        return sources

    def on_deleted(self):
        """
        apply folder deletion

        """
        session = self.session.eval()
        if not self.node_name == session:
            return False

        if not Flipbook(self.node).on_deleted():
            return False

        self.build_daillies_SID()
        session_folder = self.bdd.SID_wedger_folder_session(session=session)
        if not os.path.exists(session_folder):
            return False

        shutil.rmtree(session_folder)

    def on_name_changed(self, oldNode):
        """
        apply renaming on session folder and daillies files (sequence + mp4)
        Args:
            oldNode: the old name of the node

        """
        session = self.session.eval()
        if not self.node_name == session:
            return False

        if not self.read_version.evalAsString() == "000":
            return False

        if not self.search_release.eval():
            return False

        self.build_daillies_SID()
        session_folder = self.bdd.SID_wedger_folder_session(session=session)
        old_session_folder = os.path.join(os.path.dirname(session_folder), oldNode)
        if not os.path.exists(old_session_folder):
            return False

        os.rename(old_session_folder, session_folder)

        files_folder = os.path.dirname(self.bdd.SID_complete_daillies_path(session=session))
        if os.path.exists(files_folder):
            self._rename_files_sequence(files_folder)

        mp4_folder = os.path.dirname(self.bdd.SID_complete_daillies_mp4_path(session=session))
        if os.path.exists(mp4_folder):
            self._rename_files_mp4(mp4_folder)

    def output(self, script_padding=False, increment=False, release=False, force_sid=None):
        """
        set the output of the daillies
        Returns: the output file path

        """
        self.build_daillies_SID(script_padding=script_padding, force_sid=force_sid)
        session = self.session.eval()
        search_release = self.search_release.eval()
        if release:
            output = self.bdd.SID_release_complete_daillies_path(session=session)
            return output

        output = self.bdd.SID_complete_daillies_path(session=session)
        if search_release:
            if not increment:
                output = self.bdd.SID_release_complete_daillies_path(session=session)
            else:
                output = self.bdd.SID_complete_daillies_path(session=session)
        return output

    def output_path_mp4(self, increment=False, release=False, force_sid=None):
        """
        set the output of the daillies mp4
        Returns: the output file path

        """
        frame = self.find_frame(mp4=True)

        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_file(name=self.session.eval(), wedge_suffix=self.index.eval(), frame=frame)
        session = self.session.eval()
        search_release = self.search_release.eval()
        if release:
            output = self.bdd.SID_release_complete_daillies_mp4_path(session=session)
            return output

        output = self.bdd.SID_complete_daillies_mp4_path(session=session)
        if search_release:
            if not increment:
                output = self.bdd.SID_release_complete_daillies_mp4_path(session=session)
            else:
                output = self.bdd.SID_complete_daillies_mp4_path(session=session)

        return output

    def pdg_calculate_daillies_number(self):
        """
        prepare daillies pdg afer wedgers comptutation
        Returns: a dict of parameters to set in PDG

        """
        wedgers_node = hou.node(self.node_path + '/wedgers')
        datas = {}
        # COLLECT CURRENT DAILLIES WEDGERS
        nodes = [i for i in hou.nodeType('Top/{0}'.format(ROFL_WEDGER)).instances() if i.parent() == wedgers_node]
        for i, node in enumerate(nodes):
            iteration = str(i+1)
            iteration_loop = (i%4)+1
            wedge_node = Wedger(node)
            output = wedge_node.main_output.eval()
            output = output.split('0001')[0]
            datas["wedger{0}".format(iteration)] = {"path{0}".format(iteration_loop): output,
                                                    "switch{0}".format(iteration_loop): 1,
                                                    "index": int(i/4)}

        return datas