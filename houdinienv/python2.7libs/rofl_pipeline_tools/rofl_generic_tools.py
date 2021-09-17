import os
import shutil

import hou

from rofl_toolbox.generic_python.python_generic import Generic
from rofl_toolbox.data_base_system.sid_bdd_json import SidBdd
"""
pour le on name changed faudra utiliser la fonction get source file histoire d avoir du renaming clean
filtreage de fichier pour le  on name changed

caches = os.listdir(bgeo_path)
for i in caches:
    sid_bdd.data_base_system = "{0} | {1}".format(base_SID, i)
    cache_path = sid_bdd.SID_cache_folder_filename(format="bgeo")
    cache_path = cache_path.replace("/mnt/408C65188C650A2C", "D:")
    for file in os.listdir(cache_path):
        sid_list = sid_bdd.data_base_system.split(" | ")
        file_sid_list = sid_bdd.conform_file_for_sid(file).split(" | ")
        check = all(item in file_sid_list for item in sid_list)
        if check:
            print(file)"""


class GenericTools:
    def __init__(self, node):
        self._SID = hou.hscriptExpression("$SID")
        self.bdd = SidBdd(self.SID)
        self.node = node

    @property
    def frame_end(self):
        return self.node.parm("f2")

    @property
    def frame_start(self):
        return self.node.parm("f1")

    @property
    def main_output(self):
        return self.node.parm('main_output')

    @property
    def menu_item(self):
        return self.node.parm('menuItem')

    @property
    def node_name(self):
        return self.node.name()

    @property
    def node_path(self):
        return self.node.path()

    @property
    def node_type(self):
        return self.node.type()

    @property
    def node_type_name(self):
        return self.node_type.name()

    @property
    def override_output(self):
        return self.node.parm('overrideOutput')

    @property
    def SID(self):
        return self._SID

    @property
    def trange(self):
        return self.node.parm('trange')

    @property
    def read_version(self):
        return self.node.parm("version")

    @property
    def search_release(self):
        return self.node.parm("search_release")

    @property
    def wedge(self):
        return self.node.parm('wedge')

    @property
    def wedge_suffix(self):
        return self.node.parm('wedgeSuffix')

    def check_node_exist(self):
        """
        check if the current node has already the same name in the scene
        Returns: true if succeed
        """
        allNodeNames = [i.name() for i in self.node_type.instances() if not i.isInsideLockedHDA()]
        if len(allNodeNames) != len(sorted(set(allNodeNames))):
            message = '{0} already exist in the scene, please delete this node and rename it properly'.format(self.node_name)
            hou.ui.displayMessage(message)
            return False
        return True

    def find_frame(self, script_padding=False):
        """
        find the current frame
        Returns: frame in str format

        """
        if script_padding:
            return "$F4"

        frame = hou.frame()
        return format(int(frame), "04d")

    def find_wedge_suffix(self):
        """
        define wedge suffix
        Args:
            iteration: the iteration number to load in read multiple inputs at the same time

        Returns:suffix

        """
        suffix = ""
        if self.wedge.eval():
            suffix = self.wedge_suffix.eval()

        return suffix

    def get_source_files(self, folder=None):
        files = os.listdir(folder)
        sid_list = self.bdd.conform_sid_to_list()
        sources = [os.path.join(folder, file).replace("\\", "/") for file in files
                   if all(item in self.bdd.conform_file_to_list(file) for item in sid_list)]

        return sources

    def on_created(self):
        """
        code apply on hda creation
        """
        self.node.setColor(hou.Color([0.384, 0.184, 0.329]))

    def on_name_changed(self, oldNode):
        """
        basic code for node and files renaming
        Args:
            oldNode: the old name of the node
        """
        if hou.hipFile.isShuttingDown():
            return False
        if self.override_output.eval():
            return False
        if not self.read_version.evalAsString() == "000":
            return False
        if self.search_release.eval():
            return False

        # DEFINE OLD AND NEW FOLDER
        output = self.main_output.eval()
        folder = os.path.dirname(output)
        oldFolder = os.path.join(os.path.dirname(folder), oldNode)

        # RENAME FOLDER
        if not os.path.isdir(oldFolder):
            return False
        os.rename(oldFolder, folder)
        return folder

    def on_deleted(self):
        """
        basic code for node and files deleted
        """
        if hou.hipFile.isShuttingDown():
            return False
        if hou.hipFile.isLoadingHipFile():
            return False
        if self.override_output.eval():
            return False
        if not self.read_version.evalAsString() == "000":
            return False
        if self.search_release.eval():
            return False

        folderToDelete = os.path.dirname(self.main_output.eval())
        if not os.path.isdir(folderToDelete):
            return False

        deleteFilesInfo = hou.ui.displayMessage('Delete Files ? ({0})'.format(self.node_name), ['Yes', 'No'])
        if deleteFilesInfo == 1:
            return False

        shutil.rmtree(folderToDelete)
        return True

    def override_output_action(self):
        """
        basic code for output override on hda
        """
        override = self.override_output.eval()
        if override:
            self.main_output.deleteAllKeyframes()
        else:
            self.main_output.revertToDefaults()

    def pdg_check_version(self):
        if self.read_version.evalAsString() == "---":
            return True
        if not self.read_version.evalAsString() == "000" or self.search_release.eval():
            self.search_release.set(0)
            self.read_version.set("000")
            return False
        return True

    def show_explorer(self):
        """
        basic code for opening explorer on file location
        """
        path = self.main_output.eval()
        path = os.path.dirname(path)
        Generic().open_folder(path)

    def show_explorer_hou(self):
        """
        basic code for opening explorer on file location with houdini ui
        """
        path = self.main_output.eval()
        path = os.path.dirname(path)
        sequences = hou.ui.selectFile(start_directory=path, multiple_select=True, collapse_sequences=True)

        return sequences

    def wedge_action(self):
        """
        basic code for wedge toggle on hda
        """
        wedge = self.wedge.eval()
        if not wedge:
            self.wedge_suffix.revertToDefaults()

        return wedge