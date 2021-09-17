import os
import shutil

import hou

from rofl_pipeline_tools.rofl_filecache import FileCache
from rofl_pipeline_tools.rofl_sequencer import Sequencer
from rofl_pipeline_tools.rofl_flipbook import Flipbook
from rofl_toolbox.generic_python.softs_generic.generic_houdini.general import HouGeneral
from rofl_pipeline_tools.constants import ROFL_CACHE, ROFL_WEDGER, ROFL_SEQUENCER

class Wedger(Flipbook):
    def __init__(self, node):
        Flipbook.__init__(self, node)
        self.houGeneral = HouGeneral()
        self.extension = self.houGeneral.get_license_category()

    def __str__(self):
        if not self.node_type_name == ROFL_WEDGER:
            return "The given node isn't a rofl_wedger"
        return "success loading"

    @property
    def cacheInfos_txt(self):
        return self.node.parm("cacheInfos_txt")

    @property
    def column1_txt(self):
        return self.node.parm("column1_txt")

    @property
    def column2_txt(self):
        return self.node.parm("column2_txt")

    @property
    def column3_txt(self):
        return self.node.parm("column3_txt")

    @property
    def elements1(self):
        return self.node.parm("elements1")

    @property
    def elements2(self):
        return self.node.parm("elements2")

    @property
    def elements3(self):
        return self.node.parm("elements3")

    @property
    def enable_nb_points(self):
        return self.node.parm("enableNbPoints")

    @property
    def fileInfos_txt(self):
        return self.node.parm("fileInfos_txt")

    @property
    def frameInfos_txt(self):
        return self.node.parm("frameInfos_txt")

    @property
    def nb_points(self):
        return self.node.parm("nbPoints")

    @property
    def nbPoints_txt(self):
        return self.node.parm("nbPoints_txt")

    @property
    def override_scene(self):
        return self.node.parm("overrideScene")

    @property
    def output_scene(self):
        return self.node.parm("outputScene")

    @property
    def session(self):
        return self.node.parm("session")

    def build_wedger_scene_SID(self):
        """
        build a data_base_system for scene path
        """
        suffix = self.wedge_suffix.eval()

        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_file(name=suffix, frame="")

        return self.bdd.SID

    def build_wedger_SID(self, script_padding=False, force_sid=None):
        """
        build a sid for output file
        """
        suffix = self.wedge_suffix.eval()
        frame = self.find_frame(script_padding=script_padding)

        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString()) if not force_sid else force_sid
        self.bdd.SID = self.bdd.build_SID_file(name=suffix, frame=frame)

        return self.bdd.SID

    def _get_caches(self):
        """
        set the text for caches informations
        Returns: the cache text

        """
        text = '.: Caches Time :.\n\n'

        sequencers = hou.nodeType('Top/{0}'.format(ROFL_SEQUENCER)).instances()
        for i in sequencers:
            filecache = self._get_filecache_sequencer(item=i)
            if not filecache:
                continue

            simTime = "`@{0}`".format(filecache.node_name)
            text += '''{0} : {1}'''.format(filecache.node_name, simTime) + '\n\n'

        return text

    def _get_column(self, head="", number="0", nb_elements=0):
        """
        set the text for elements part
        Returns: the text

        """
        text = "{0}\n\n".format(head)
        for i in range(nb_elements):
            iteration = str(i+1)

            cur_node = self._node_iteration(iteration, number)
            if not cur_node:
                continue

            text += cur_node.path() + '\n\n'
            # GET PARMS
            nb_parms = self.node.parm('parms{0}_{1}'.format(iteration, number)).eval()
            for j in range(nb_parms):
                iteration2 = str(j + 1)
                parm = self.node.parm('parm{0}_{1}_{2}'.format(iteration, iteration2, number))
                parm_name = parm.eval()
                if not hou.parm("{0}/{1}".format(cur_node.path(), parm_name)) and parm_name != "":
                    self._message_info("Please set a correct parm for {0}".format(parm.name()))
                    continue

                value = 'value{0}_{1}_{2}'.format(iteration, iteration2, number)
                text += '''    {0} = `chs("{1}/{2}")`'''.format(parm_name, self.node_path, value) + '\n'
            text += '\n'

        return text

    def _get_filecache_sequencer(self, item):
        """
        get a filecache instance according to the nodePath sequencer
        Args:
            item: the sequencer

        Returns: filecache instance

        """
        # check if the sequencer is inside the current rofl_wedger
        if not self.node == item.parent().parent():
            return False
        # check if the node path of the sequencer points on an existing node
        sequencer = Sequencer(item)
        filecache_node = sequencer.rop_node_path.evalAsNode()
        if not filecache_node:
            print('Please Set a Correct Node Path on Sequencer')
            return False
        # check if the given node is a rofl_filecache
        if not filecache_node.type().name() == ROFL_CACHE:
            print("Please give a rofl_filecache to the sequencer {0}".format(sequencer.node_path))
            return False

        return FileCache(filecache_node)

    def _get_frames(self):
        """
        set the text for frame part
        Returns: the text

        """
        frame_text = 'Frame : $F4'
        return frame_text

    def _get_nb_points(self):
        """
        set the text for nb points part
        Returns: the text

        """
        text = ""
        path = self.nb_points.evalAsNode().path() if self.nb_points.evalAsNode() else self.nb_points.eval()
        if not self.nb_points.evalAsNode() and path != "" and self.enable_nb_points.eval():
            self._message_info("Please, set a correct path for this parameter")
            return text

        nb_points_text = '''Number of Points : `npoints("{0}")`'''.format(path)
        text = nb_points_text if self.enable_nb_points.eval() else ""

        return text

    def _get_scene_name(self):
        """
        set the text for scene name part
        Returns: the text

        """
        scene_name = os.path.basename(self.output_scene.eval())
        scene_name = scene_name.split(".")[0]
        return scene_name

    def _link_parameters_by_column(self, number="0", nb_elements=0, clean=False):
        """
        basic code for links pdg with sops
        Args:
            number: the number of the column in str
            nb_elements: valu of self.elements(number)
            clean: tells if we clean the SOP scene parameters from PDG links

        """
        for i in range(nb_elements):
            iteration = str(i + 1)

            cur_node = self._node_iteration(iteration, number)
            if not cur_node:
                continue

            nb_parms = self.node.parm('parms{0}_{1}'.format(iteration, number)).eval()
            for j in range(nb_parms):
                iteration2 = str(j + 1)
                parm_path = 'parm{0}_{1}_{2}'.format(iteration, iteration2, number)
                value_path = 'value{0}_{1}_{2}'.format(iteration, iteration2, number)
                # GET THE VALUE
                parm_name = self.node.parm(parm_path).eval()
                self._set_link_values(cur_node, parm_name, value_path, clean=clean)

    def _message_info(self, message):
        try:
            hou.ui.displayMessage(message)
        except:
            print(message)

    def _node_iteration(self, iteration, number):
        """
        check if the given node is correct
        Args:
            iteration: iteration of parms
            number: the number of the column

        Returns: node if succeed

        """
        node_parm = self.node.parm('node{0}_{1}'.format(iteration, number))
        node = node_parm.evalAsNode()
        if not node:
            self._message_info('{0} has not a correct path'.format(node_parm.name()))
            return False
        return node

    def _pdg_get_elements(self, number="0", nb_elements=0):
        """
        get all the parameters and according values
        Args:
            number: the number of the column
            nb_elements: the value of nbelements on the column

        Returns: dict of parms and values

        """
        datas = {}
        # SET ATTRIBUTES ACCORDING TO THE UI
        for i in range(nb_elements):
            iteration = str(i + 1)
            # GET CURRENT NODE AND HIS PARMS
            nbParms = self.node.parm('parms{0}_{1}'.format(iteration, number)).eval()
            for j in range(nbParms):
                iteration2 = str(j + 1)
                # GET THE VALUE
                parmName = self.node.parm('parm{0}_{1}_{2}'.format(iteration, iteration2, number)).eval()
                parmValue = self.node.parm('value{0}_{1}_{2}'.format(iteration, iteration2, number)).path()
                datas[parmName] = parmValue

        return datas

    def _set_link_values(self, node, parm_name, value_path, clean=False):
        """
        link hda values with the according sop values
        Args:
            node: node to apply values
            parm_name: the name of the parm to apply values
            value_path: the hda value path to `chs`
            clean: tells if we clean the SOP scene parameters from PDG links

        """
        if not clean:
            node.parm(parm_name).setExpression('''ch("`@{0}`")'''.format(parm_name))
            self.generate_layout()
        else:
            if self.node.parm(value_path).keyframes() == ():
                # SET SIMPLE VALUE
                parm_value = self.node.parm(value_path).eval()
                node.parm(parm_name).deleteAllKeyframes()
                node.parm(parm_name).set(parm_value)
            else:
                # DUPLICATE ANIMATION
                parm_src = self.node.parm(value_path)
                parm_dst = node.parm(parm_name)
                parm_dst.deleteAllKeyframes()
                for k in parm_src.keyframes():
                    parm_dst.setKeyframe(k)
            # CLEAN WEDGE CACHE
            self.activate_cache_wedges(True)

    def activate_cache_wedges(self, clean=False):
        """
        set the wedge and wedge suffix parameter on filecache which are binds with the according sequencer
        used with the apply wedge suffix on caches parameter
        Args:
            clean: tells if we clean the SOP scene parameters from PDG links

        """
        sequencers = hou.nodeType('Top/{0}'.format(ROFL_SEQUENCER)).instances()
        for i in sequencers:
            filecache = self._get_filecache_sequencer(item=i)
            if not filecache:
                continue

            wedge = self.wedge.eval()
            filecache.wedge.set(wedge)
            if clean:
                filecache.wedge_suffix.set(self.wedge_suffix.eval())
                filecache.link_layers.set(wedge)
                continue

            filecache.wedge_suffix.set("`@wedgeSuffix`")
            filecache.wedge_action()

        self.generate_layout()

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

        if self.node.parent().name() == "wedgers":
            daillies_node = self.node.parent().parent()
            menu = daillies_node.parm("menuItem").eval()
            versions_list = menu.split()
        else:
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

    def generate_layout(self):
        """
        build the text for the watermarks and set the according parameters
        used by multiple parameters to build the watermarks frequently
        """
        self.column1_txt.set(self._get_column(head=".: PARAMETERS :.", number=1, nb_elements=self.elements1.eval()))
        self.column2_txt.set(self._get_column(number=2, nb_elements=self.elements2.eval()))
        self.column3_txt.set(self._get_column(number=3, nb_elements=self.elements3.eval()))
        self.fileInfos_txt.set(self._get_scene_name())
        self.cacheInfos_txt.set(self._get_caches())
        self.frameInfos_txt.set(self._get_frames())
        self.nbPoints_txt.set(self._get_nb_points())

    def get_copy_files_infos(self, sid_src_version=None, sid_tgt_version=None, release=False):
        files = {}

        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_name(self.wedge_suffix.eval())
        if not self.search_release.eval():
            folder = self.bdd.SID_wedger_folder_name(session=self.session.eval())
        else:
            folder = self.bdd.SID_release_wedger_folder_name(session=self.session.eval())
        if not os.path.isdir(folder):
            return files

        file_sources = self.get_source_files(folder=folder)
        for file in file_sources:
            filename = os.path.basename(file)
            self.bdd.SID = self.bdd.conform_file_for_sid(filename)
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)

            if not release:
                tgt = self.bdd.SID_complete_wedger_path(session=self.session.eval())
            else:
                tgt = self.bdd.SID_release_complete_wedger_path(session=self.session.eval())
            files[filename] = {"src": file, "tgt": tgt}

        # GET SCENE
        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_file(self.wedge_suffix.eval(), frame="")
        if not self.search_release.eval():
            folder = self.bdd.SID_wedger_folder_session(session=self.session.eval())
        else:
            folder = self.bdd.SID_release_wedger_folder_session(session=self.session.eval())
        if not os.path.isdir(folder):
            return files

        scene_source = self.get_source_files_scene()
        if os.path.exists(scene_source):
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)
            if not release:
                tgt = self.bdd.SID_wedger_scene_complete(session=self.session.eval()) + ".{0}".format(self.extension)
            else:
                tgt = self.bdd.SID_release_wedger_scene_complete(session=self.session.eval()) + ".{0}".format(self.extension)
            files[os.path.basename(scene_source)] = {"src": scene_source, "tgt": tgt}

        return files

    def get_source_files(self, folder=None):
        files = os.listdir(folder)
        sid_list = self.bdd.conform_sid_to_list()
        sources = [os.path.join(folder, file).replace("\\", "/") for file in files if all(item in self.bdd.conform_file_to_list(file) for item in sid_list)]

        return sources

    def get_source_files_scene(self):
        sources = self.bdd.SID_wedger_scene_complete(session=self.session.eval()) + ".{0}".format(self.extension)

        return sources

    def link_parameters(self, clean=False):
        """
        links all the wedger parameters to their according SOP parameters for PDG computing
        used by values parameters to set the scene for PDG
        Args:
            clean: tells if we clean the SOP scene parameters from PDG links

        """
        self._link_parameters_by_column(number="1", nb_elements=self.elements1.eval(), clean=clean)
        self._link_parameters_by_column(number="2", nb_elements=self.elements2.eval(), clean=clean)
        self._link_parameters_by_column(number="3", nb_elements=self.elements3.eval(), clean=clean)
        self.generate_layout()

    def on_created(self):
        Flipbook(self.node).on_created()
        self.generate_layout()

    def on_deleted(self):
        """
        classic on_deleted function + scene deletion

        """
        if self.node.parent().name() == "wedgers":
            return False

        if not Flipbook(self.node).on_deleted_base():
            return False

        cleanScene = hou.ui.displayMessage('Clean TOP links With Houdini Scene ? ({0})'.format(self.node_name), ['Yes', 'No'])
        if cleanScene == 0:
            self.link_parameters(clean=True)

        if self.override_scene.eval():
            return False

        scene_path = self.output_scene.eval()
        if not os.path.exists(scene_path):
            return False

        os.remove(scene_path)

    def on_input_changed(self):
        self.generate_layout()

    def on_name_changed(self, oldNode):
        """
        rename the session folder if the wedger is not inside a rofl_daillies and if the session parameter
        is set on the name of the wedger
        Args:
            oldNode: the name before renaming

        """
        self.generate_layout()
        session = self.session.eval()
        if not self.node_name == session:
            return False

        if self.node.parent().name() == "wedgers":
            return False

        if not self.read_version.evalAsString() == "000":
            return False

        if not self.search_release.eval():
            return False

        self.build_wedger_SID()
        session_folder = self.bdd.SID_wedger_folder_session(session=session)
        old_session_folder = os.path.join(os.path.dirname(session_folder), oldNode)
        if not os.path.exists(old_session_folder):
            return False

        os.rename(old_session_folder, session_folder)

    def output(self, script_padding=False, increment=False, release=False, force_sid=None):
        """
        set the output of the wedger
        Returns: the output file path

        """
        self.build_wedger_SID(script_padding=script_padding, force_sid=force_sid)
        session = self.session.eval()
        search_release = self.search_release.eval()
        if release:
            output = self.bdd.SID_release_complete_wedger_path(session=session)
            return output

        output = self.bdd.SID_complete_wedger_path(session=session)
        if search_release:
            if not increment:
                output = self.bdd.SID_release_complete_wedger_path(session=session)
            else:
                output = self.bdd.SID_complete_wedger_path(session=session)

        return output

    def output_blast(self):
        """
        the output for temporary wedger
        Returns: path of the output
        """
        self.build_wedger_SID()
        session = self.session.eval()
        output = self.bdd.SID_complete_wedger_tmp_path(session=session)

        return output

    def output_path_scene(self, increment=False, release=False, force_sid=None):
        """
        set the output of the wedger scene
        Returns: the output file path

        """
        self.build_wedger_SID(force_sid=force_sid)
        session = self.session.eval()
        search_release = self.search_release.eval()
        if release:
            output = self.bdd.SID_release_wedger_scene_complete(session=session)
            return output

        output = self.bdd.SID_wedger_scene_complete(session=session)
        if search_release:
            if not increment:
                output = self.bdd.SID_release_wedger_scene_complete(session=session)
            else:
                output = self.bdd.SID_wedger_scene_complete(session=session)

        output += "." + self.extension

        return output

    def override_scene_action(self):
        """
        basic code for output override on hda
        """
        override = self.override_scene.eval()
        if override:
            self.output_scene.deleteAllKeyframes()
        else:
            self.output_scene.revertToDefaults()

    def parm_finder(self, kwargs):
        """
        build a Houdini UI to search parameters according to the corresponding node
        used with the little gears on the hda next to the name parameter
        Args:
            kwargs: the kwargs from the parameter which trigger this function

        """
        # GET BUTTON ID
        id = kwargs['parm_name'].split('parmFinder')[-1]
        # GET THE NODE TO SEARCH PARMS
        node_id = id.split('_')[0]
        node_section = id.split('_')[-1]
        node = self._node_iteration(node_id, node_section)
        if not node:
            return False

        # GET FIRST PARM
        first_parm = [node.parms()[1]]
        # Build up the initial selection dictionary.
        initial_selection = {"Parameters": first_parm}
        # Prompt the user to select node data.
        selected_data = hou.ui.selectNodeData(initial_selection=initial_selection,
                                              multiple_select=False,
                                              width=400,
                                              height=600,
                                              include_data_type_headers=False,
                                              include_object_transforms=False,
                                              include_geometry_bounding_boxes=False,
                                              include_geometry_attributes=False)
        parm_name = selected_data['Parameters'][0].name()
        self.node.parm('parm' + id).set(parm_name)
        # GENERATE LAYOUT
        self.generate_layout()
        self.link_parameters()

    def pdg_clean_and_save_scene(self):
        """
        modify the scene in command line to break all the connections between PDG and SOPS
        used in PDG by houdini server command line

        """
        self.activate_cache_wedges(clean=True)
        self.link_parameters(clean=True)

        scene_path = self.output_scene.eval()
        folder = os.path.dirname(scene_path)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        hou.hipFile.save(scene_path)

    def pdg_delete_tmp_folder(self):
        """
        delete the tmp flipbook when wedger is done
        used in PDG

        """
        folder = os.path.dirname(self.output_blast())
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    def pdg_get_sims_time(self):
        """
        get the cache time on sequencers inside the wedger
        used in PDG

        """
        datas = {}
        for i in hou.nodeType('Top/{0}'.format(ROFL_SEQUENCER)).instances():
            filecache = self._get_filecache_sequencer(item=i)
            if not filecache:
                continue

            time_spend = i.parm('simTime').eval()
            datas[filecache.node_name] = time_spend

        return datas

    def pdg_prepare_wedger(self):
        """
        get all the necessary datas for PDG computation
        used in PDG

        """
        datas = {}
        datas.update(self._pdg_get_elements(number="1", nb_elements=self.elements1.eval()))
        datas.update(self._pdg_get_elements(number="2", nb_elements=self.elements2.eval()))
        datas.update(self._pdg_get_elements(number="3", nb_elements=self.elements3.eval()))
        datas.update({"wedgeSuffix": self.wedge_suffix.evalAsString()})
        return datas

