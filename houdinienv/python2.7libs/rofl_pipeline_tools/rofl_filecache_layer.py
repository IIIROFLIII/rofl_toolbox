import os

import hou

from rofl_pipeline_tools.rofl_generic_tools import GenericTools
from rofl_toolbox.data_base_system.constants import SID_FILE_SEPARATOR
from rofl_pipeline_tools.constants import ROFL_CACHE, ROFL_CACHE_LAYER

class FileCacheLayer(GenericTools):
    def __init__(self, node):
        GenericTools.__init__(self, node)

    def __str__(self):
        if not self.node_type_name == ROFL_CACHE_LAYER:
            return "The given node isn't a rofl_filecache_layer"
        return "success loading"

    @property
    def cache_version(self):
        return self.node.parm('cacheVersion')

    @property
    def file_geo(self):
        return hou.node(self.node_path + '/file1')

    @property
    def geo_type(self):
        return self.node.parm('geometryType')

    @property
    def multiple_inputs(self):
        return self.node.parm('readMultiInput')

    @property
    def wedge_inputs(self):
        return self.node.parm('wedgeInputs')

    @property
    def wedge_suffix(self):
        return self.node.parm('wedgeSuffix')

    def check_node_exist(self):
        """
        check if a filecache has already the same name in the scene
        Returns: true if succeed
        """
        allCachesNames = [i.name() for i in hou.nodeType('Sop/{0}'.format(ROFL_CACHE)).instances()]
        allCachesNames += [i.name() for i in hou.nodeType('Sop/{0}'.format(ROFL_CACHE_LAYER)).instances()]
        if len(allCachesNames) != len(sorted(set(allCachesNames))):
            message = '{0} already exist in the scene, please delete this node and rename it properly'.format(self.node_name)
            hou.ui.displayMessage(message)
            return False
        return True

    def find_wedge_suffix(self, iteration=0):
        """
        define wedge suffix
        Args:
            iteration: the iteration number to load in read multiple inputs at the same time

        Returns:suffix

        """
        suffix = GenericTools(self.node).find_wedge_suffix()
        if self.multiple_inputs.eval():
            values = self.wedge_inputs.eval().split(' ')
            suffix = values[iteration]

        return suffix

    def find_version_files(self):
        """
        list all cache version available in increment sections
        Returns: a liste for houdini menu
        """
        if self.override_output.eval():
            return ["---", "---"]

        self.menu_item.set('')
        search_release = self.search_release.eval()
        versions_list = self.bdd.get_incr_caches_version_list(self, release=search_release)
        for i in versions_list:
            self.menu_item.set("{0} {1}".format(self.menu_item.eval(), i))

        # BUILD MENU FOR "MENU SCRIPT WORKING"
        menuitems = self.menu_item.eval().split()
        menu = ["000", "000"]
        for item in menuitems:
            menu.append(item)
            menu.append(item)

        return menu

    def get_all_wedges_names(self, script_padding=False, increment=False, release=False, force_sid=None):
        wedge_inputs = self.wedge_inputs.eval().split(" ")
        wedge_inputs.remove("")
        outputs = []

        if not wedge_inputs:
            path = self.output(script_padding=script_padding, increment=increment, force_sid=force_sid, release=release)
            name = os.path.basename(path)
            outputs.append(name)
            return outputs

        for i in wedge_inputs:
            path = self.output(script_padding=script_padding, increment=increment, force_sid=force_sid,
                               force_suffix=i, release=release)
            name = os.path.basename(path)
            outputs.append(name)
        return outputs

    def get_version_cache(self):
        """
        copy incremented cache in work 000 folder
        """
        version = self.cache_version.eval()
        if version == 0:
            return False
        # la faudra le systeme de copie de fichiers
        print("WIP")
        # elements = {}
        # # ROFL CACHE
        # if node.type().name() == 'rofl_cache':
        #     elements = get_rofl_cache(node, elements, False)
        # # ROFL CACHES LAYER
        # if node.type().name() == 'rofl_cache_layer':
        #     elements = get_rofl_cache_layer(node, elements, False)
        # # COPY FILES
        # SMNodeType.hdaModule().launch_batch_copy(elements)

    def get_copy_files_infos(self, sid_src_version=None, sid_tgt_version=None, release=False):
        files = {}

        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_name(self.node_name)
        if not self.search_release.eval():
            folder = self.bdd.SID_cache_folder_filename(self.geo_type.evalAsString())
        else:
            folder = self.bdd.SID_release_cache_folder_filename(self.geo_type.evalAsString())
        if not os.path.isdir(folder):
            return files

        file_sources = self.get_source_files(folder=folder)
        if not file_sources:
            return files
        
        for file in file_sources:
            filename = os.path.basename(file)
            self.bdd.SID = self.bdd.conform_file_for_sid(filename)
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)

            file_format = self.geo_type.evalAsString()
            if not release:
                tgt = self.bdd.SID_complete_cache_path(geo_type=file_format)
            else:
                tgt = self.bdd.SID_release_complete_cache_path(geo_type=file_format)

            files[filename] = {"src": file, "tgt": tgt}

        return files

    def on_name_changed(self, oldNode):
        """
        additional rules for renaming
        """
        if self.geo_type.evalAsString() == 'abc':
            return False
        if not self.check_node_exist():
            return False

        folder = GenericTools(self.node).on_name_changed(oldNode)
        if not folder:
            return False

        # RENAME FILES
        for i in os.listdir(folder):
            if len(i.split(SID_FILE_SEPARATOR)) != 6:
                continue

            extension = os.path.splitext(i)[1][1:]
            if extension == "sc":
                extension = "bgeo"

            self.bdd.SID = self.bdd.conform_file_for_sid(i)
            self.bdd.SID = self.bdd.sid_replace_filename(self.node_name)

            isSequence = 1 if self.bdd.SID_frame else 0
            new_file = self.bdd.SID_complete_cache_path(geo_type=extension, abc_sequence=isSequence)
            os.rename(os.path.join(folder, i), os.path.join(folder, new_file))

    def on_deleted(self):
        """
        additional rules for deleting
        """
        if self.geo_type.evalAsString() == 'abc':
            return False
        if not GenericTools(self.node).on_deleted():
            return False

    def output(self, iteration=0, script_padding=False, increment=False, release=False, force_sid=None, force_suffix=None):
        """
        set the output of the filecache
        Returns: the output file path

        """

        format = self.geo_type.evalAsString()
        suffix = force_suffix if force_suffix else self.find_wedge_suffix(iteration=iteration)
        frame = self.find_frame(script_padding=script_padding)
        search_release = self.search_release.eval()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString()) if not force_sid else force_sid
        self.bdd.SID = self.bdd.build_SID_file(name=self.node_name, wedge_suffix=suffix, frame=frame)

        if release:
            output = self.bdd.SID_release_complete_cache_path(geo_type=format)
            return output

        output = self.bdd.SID_complete_cache_path(geo_type=format)
        if search_release:
            if not increment:
                output = self.bdd.SID_release_complete_cache_path(geo_type=format)
            else:
                output = self.bdd.SID_complete_cache_path(geo_type=format)

        return output

    def reload(self):
        """
        reload file or alembic sop in the filecache
        """
        self.file_geo.parm('reload').pressButton()

    def select_inputs(self):
        """
        load multiple cache at the same time with different wedge suffix values
        """
        if not self.multiple_inputs.eval():
            return False

        if self.override_output.eval():
            return False

        path = self.main_output.eval()
        folder = os.path.dirname(path)

        inputs = hou.ui.selectFile(start_directory=folder, multiple_select=True, collapse_sequences=True)
        inputs = inputs.split(';')
        if len(inputs) == 1 and inputs[0] == '':
            self.multiple_inputs.set(0)
            return True

        array = ''
        for i in inputs:
            seq = i.replace(' ', '')
            file = os.path.basename(seq)
            self.bdd.SID = self.bdd.conform_file_for_sid(file)
            wedgesSuffix = "{0} ".format(self.bdd.SID_wedge_suffix)
            array += wedgesSuffix

        self.wedge_inputs.set(array)