import os
import datetime
import getpass
from glob import glob

from rofl_toolbox.file_manager.constants import MSG
from rofl_toolbox.data_base_system.sid_paths import SidPaths
from rofl_toolbox.data_base_system.sid_interpreter import SidInterpreter, sid_generic
from rofl_toolbox.data_base_system.constants import SID_SEPARATOR
from rofl_toolbox.generic_python.python_generic import Generic
from rofl_toolbox.data_base_system.constants import CACHES, FLIPBOOKS, RENDERS, WEDGES

class SidBdd(SidPaths):
    def __init__(self, sid=sid_generic()):
        SidPaths.__init__(self, sid)
        self._data = {}
        self.refresh_data()

    @property
    def data(self):
        return self._data

    def _check_complete_sid(self):
        """
        check if the data_base_system has all the values necessary to build the scene ID
        Returns: True if succeed

        """
        if "xxx" in self.SID:
            msg = MSG["SID_NOT_COMPLETE"]
            return False, msg
        return True, ""

    def _check_project_exist(self):
        """
        check if the project exist or not
        Returns: True if success

        """
        if self.SID_projectAlias in self._get_project_list():
            return True, ""

        msg = MSG["PROJECT_NOT_EXIST"]
        return False, ""

    def _check_scene_exist(self):
        """
        check if the scene exist
        Returns: True if success

        """
        if self.data.get(self.SID) == None:
            return False
        return True

    def _checks_primary(self):
        """
        apply multiple checks in one function
        Returns: True if success

        """
        check_sid, log = self._check_complete_sid()
        if not check_sid:
            return False, log
        check_project, log = self._check_project_exist()
        if not check_project:
            return False, log
        return True, ""

    def _delete_scene_grp(self, software, scenes):
        """
        delele all the given scenes in the database
        Args:
            software: the software used
            scenes: a liste of the scenes to delete
        """
        sid_liste = self._get_list_sid(software, scenes)
        for i in sid_liste:
            del self.data[i]

        self._save_project(self.data)

    def _get_project_list(self):
        """

        Returns: recupere la liste de tous les groupes de projets

        """
        projects = glob(os.path.join(os.path.dirname(self.project_path), "*.json"))
        return [os.path.splitext(os.path.basename(i))[0] for i in projects]

    def _get_list_element(self, software, scenes, element):
        """
        get a list element of sid filtered for a choosen software
        Args:
            software: software to filter with
            scenes: list of data_base_system
            element: type of data_base_system element

        Returns: the filtered list elements with data_base_system

        """
        if software != None:
            liste = [eval("SidInterpreter(i).{0}".format(element)) for i in scenes if SidBdd(i).data[i].get("software") == software]
        else:
            liste = [eval("SidInterpreter(i).{0}".format(element)) for i in scenes]
        liste = sorted(set(liste))

        return liste

    def _get_list_sid(self, software, scenes):
        """
        get a list of sid filtered for a choosen software
        Args:
            software: software to filter with
            scenes: list of data_base_system

        Returns: the filtered list with data_base_system

        """
        if software != None:
            liste = [i for i in scenes if SidBdd(i).data[i].get("software") == software]
        else:
            liste = [i for i in scenes]
        liste.sort()

        return liste

    def _get_scenes(self, release=False):
        """

        Returns: all data_base_system in a project

        """
        scenes = [i for i in self.data.keys() if len(i.split(SID_SEPARATOR)) == len(sid_generic().split(SID_SEPARATOR))]
        if release:
            scenes = [i for i in scenes if self.data[i]["release"]]
        return scenes

    def _get_scenes_task(self):
        """

        Returns: all data_base_system project which correspond to the current data_base_system with the name element

        """
        scenes = self._get_scenes()
        scenes = [i for i in scenes if SidInterpreter(i).SID_name == self.SID_name]

        return scenes

    def _get_scenes_step(self):
        """

        Returns: all data_base_system project which correspond to the current data_base_system with the name and task element

        """
        scenes = self._get_scenes()
        scenes = [i for i in scenes if SidInterpreter(i).SID_name == self.SID_name\
                                    and SidInterpreter(i).SID_task == self.SID_task]

        return scenes

    def _get_scenes_version(self, release=False):
        """

        Returns: all data_base_system project which correspond to the current data_base_system with the name, task and step elements

        """
        scenes = self._get_scenes(release=release)
        scenes = [i for i in scenes if SidInterpreter(i).SID_name == self.SID_name\
                                    and SidInterpreter(i).SID_task == self.SID_task\
                                    and SidInterpreter(i).SID_step == self.SID_step]

        return scenes

    def _get_commentary(self):
        """

        Returns: get commentary according to sid scene

        """
        commentary = ""
        if self.data.get(self.SID):
            commentary = self.data[self.SID].get("commentaries")

        return commentary

    def _get_files(self):
        """

        Returns: get files according to sid scene

        """
        files = {}
        if not self.data.get(self.SID):
            return files

        files = self.data[self.SID]

        return files

    def _get_files_path(self, file, category, release):
        file_path = ""
        extension = os.path.splitext(file)[-1][1:]
        extension = "bgeo" if extension == "sc" else extension
        self.SID = self.conform_file_for_sid(file)
        self.refresh_data()

        if category == CACHES:
            if not release:
                file_path = self.SID_complete_cache_path(geo_type=extension)
            else:
                file_path = self.SID_release_complete_cache_path(geo_type=extension)
        elif category == FLIPBOOKS:
            if not release:
                file_path = self.SID_complete_flipbook_path(format=extension)
            else:
                file_path = self.SID_release_complete_flipbook_path(format=extension)
        elif category == RENDERS:
            if not release:
                file_path = self.SID_complete_render_path(format=extension)
            else:
                file_path = self.SID_release_complete_render_path(format=extension)
        elif category == WEDGES:
            if not release:
                file_path = self.SID_complete_daillies_path(session=self.SID_filename)
            else:
                file_path = self.SID_release_complete_daillies_path(session=self.SID_filename)

        return file_path

    def _get_files_release(self):
        """

        Returns: get files according to sid scene

        """
        files = {}
        if not self.data.get(self.SID):
            return files

        if not self.data[self.SID].get("release"):
            return files

        files = self.data[self.SID]["release"]

        return files

    def _save_project(self, data):
        """
        save a json file
        Args:
            data: json datas
        """
        Generic().save_json(data_file=self.project_path, data=data)
        self.refresh_data()

    def _signature(self):
        """

        Returns: the signature apply after commentaries

        """
        user = getpass.getuser()
        date = str(datetime.datetime.now())
        signature = "\n\n----------------\nscene generated by {0} at {1}".format(user.capitalize(), date)

        return signature

    def add_files_prepare_release(self, files, release):
        """
        prepare release part to files
        Args:
            files: which files to potentially add release
            release: tell if release or not

        Returns: files datas with release status

        """
        if not release:
            return files
        if files.get("release"):
            return files

        files.update({"release": {}})
        return files

    def add_files_prepare_caches(self, datas, files, release, incr_sid):
        """
        prepare cache database
        Args:
            datas: the datas
            files: which files
            release: tell if release or not
            incr_sid: the incr sid value

        """
        self.add_files_prepare_release(files=files, release=release)
        for item in datas[CACHES]:
            if not release:
                if not files.get(CACHES):
                    files.update({CACHES: {}})

                files[CACHES].update({item.node_name: {"path": item.node_path}})
                # pour le read multiple input, faire que on prend pas le path complet
                # juste le nom du fichier, et selon le nombre d entree (ex 001 002 003) on pourra builder tous les
                # chemins, stand by pour le moment
                file_name = item.get_all_wedges_names(script_padding=True, force_sid=incr_sid, increment=True)
                # file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, increment=True))
                files[CACHES][item.node_name].update({"file_name": file_name})
            else:
                if not files["release"].get(CACHES):
                    files["release"].update({CACHES: {}})
                files["release"][CACHES].update({item.node_name: {"path": item.node_path}})
                file_name = item.get_all_wedges_names(script_padding=True, force_sid=incr_sid, release=True)
                # file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, release=release))
                files["release"][CACHES][item.node_name].update({"file_name": file_name})

    def add_files_prepare_flipbooks(self, datas, files, release, incr_sid):
        """
        prepare flipbooks database
        Args:
            datas: the datas
            files: which files
            release: tell if release or not
            incr_sid: the incr sid value

        """
        for item in datas[FLIPBOOKS]:
            if not release:
                if not files.get(FLIPBOOKS):
                    files.update({FLIPBOOKS: {}})

                files[FLIPBOOKS].update({item.node_name: {"path": item.node_path}})
                file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, increment=True))
                files[FLIPBOOKS][item.node_name].update({"file_name": file_name})
            else:
                if not files["release"].get(FLIPBOOKS):
                    files["release"].update({FLIPBOOKS: {}})

                files["release"][FLIPBOOKS].update({item.node_name: {"path": item.node_path}})
                file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, release=release))
                files["release"][FLIPBOOKS][item.node_name].update({"file_name": file_name})

    def add_files_prepare_renders(self, datas, files, release, incr_sid):
        """
        prepare renders database
        Args:
            datas: the datas
            files: which files
            release: tell if release or not
            incr_sid: the incr sid value

        """
        for item in datas[RENDERS]:
            if not release:
                if not files.get(RENDERS):
                    files.update({RENDERS: {}})

                files[RENDERS].update({item.node_name: {"path": item.node_path}})
                file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, increment=True))
                files[RENDERS][item.node_name].update({"file_name": file_name})
            else:
                if not files["release"].get(RENDERS):
                    files["release"].update({RENDERS: {}})

                files["release"][RENDERS].update({item.node_name: {"path": item.node_path}})
                file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, release=release))
                files["release"][RENDERS][item.node_name].update({"file_name": file_name})

    def add_files_prepare_wedges(self, datas, files, release, incr_sid):
        """
        prepare wedges database
        Args:
            datas: the datas
            files: which files
            release: tell if release or not
            incr_sid: the incr sid value

        """
        for item in datas[WEDGES]:
            if not release:
                if not files.get(WEDGES):
                    files.update({WEDGES: {}})

                files[WEDGES].update({item.node_name: {"path": item.node_path}})
                file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, increment=True))
                files[WEDGES][item.node_name].update({"file_name": file_name})
            else:
                if not files["release"].get(WEDGES):
                    files["release"].update({WEDGES: {}})

                files["release"][WEDGES].update({item.node_name: {"path": item.node_path}})
                file_name = os.path.basename(item.output(script_padding=True, force_sid=incr_sid, release=release))
                files["release"][WEDGES][item.node_name].update({"file_name": file_name})

    def add_files(self, files):
        """
        add files to bdd
        Args:
            files: the files elements to add

        Returns: True if succeed

        """
        if not self._check_scene_exist():
            return False

        self.data[self.SID].update(files)
        self._save_project(self.data)
        return True

    def commentaries(self, text):
        """
        add a commentary with a signature
        Args:
            text: commentary

        Returns: commentary + signature

        """
        commentary = text + self._signature()

        return commentary

    def create_project(self, alias=None, path=None):
        """
        add project group to database
        Args:
            alias: alias of the project
            path: folder path where projects files will be saved

        Returns: True if succeed

        """
        if alias == None:
            msg = MSG["SET_ALIAS"]
            return False, msg

        if path == None:
            msg = MSG["SET_PROJECT_PATH"]
            return False, msg

        if os.path.exists(self.project_path):
            msg = MSG["PROJECT_EXIST"]
            return False, msg

        if not os.path.exists(os.path.dirname(self.project_path)):
            os.makedirs(os.path.dirname(self.project_path))

        data = {"path": path}
        self._save_project(data)
        msg = ""
        return True, msg

    def create_scene(self, software=None, commentaries=None, release={}):
        """
        create scene in database
        Args:
            software: Software Used
            commentaries: commentaries attach to the scene

        Returns: True if succeed

        """
        if software == None:
            msg = MSG["SOFTWARE_NOT_GIVEN"]
            return False, msg
        if commentaries == None:
            msg = MSG["COMMENTARIES_NOT_GIVEN"]
            return False, msg
        checks, log = self._checks_primary()
        if not checks:
            msg = log
            return False, msg
        if self._check_scene_exist():
            msg = "{0} {1}".format(self.SID, MSG["SCENE_EXIST"])
            return False, msg

        self.data.update({self.SID: {"software": software,
                                     "commentaries": self.commentaries(commentaries),
                                     "release": release}})
        self._save_project(self.data)
        msg = ""
        return True, msg

    def delete_project(self):
        """
        delete project group in the database
        Returns: True if succeed
        """
        if not os.path.exists(self.project_path):
            msg = MSG["NO_PROJECT"]
            return False, msg

        os.remove(self.project_path)
        self._data = {}
        return True, ""

    def delete_scene(self):
        """
        delete scene in the database
        Returns: True if succeed
        """
        success, log = self._checks_primary()
        if not success:
            return False, log

        if not self._check_scene_exist():
            msg = "Scene {0} doesn't exist".format(self.SID)
            return False, msg

        del self.data[self.SID]
        self._save_project(self.data)
        return True, ""

    def delete_all_names(self, software=None):
        """
        delete all scenes which match project group and project name
        Args:
            software: software used
        """
        scenes = self._get_scenes()
        self._delete_scene_grp(software, scenes)

    def delete_all_tasks(self, software=None):
        """
        delete all scenes which match project group and project name and project task
        Args:
            software: software used
        """
        scenes = self._get_scenes_task()
        self._delete_scene_grp(software, scenes)

    def delete_all_steps(self, software=None):
        """
        delete all scenes which match project group and project name and project task and project step
        Args:
            software: software used
        """
        scenes = self._get_scenes_step()
        self._delete_scene_grp(software, scenes)

    def delete_all_versions(self, software=None):
        """
        delete all scenes which match project group and project name and project task and project step and versions
        Args:
            software: software used
        """
        scenes = self._get_scenes_version()
        self._delete_scene_grp(software, scenes)

    def increment_sid(self, software=None):
        """
        rebuild data_base_system with the new Increment data_base_system
        Args:
            software: software used

        Returns: the increment version

        """
        new_version = "000"
        versions = self.get_scenes_version_list(software=software)

        if len(versions):
            last_version = sorted(versions)[-1]
            new_version = format(int(last_version) + 1, "03d")

        sid_list = self.conform_sid_to_list()
        sid_list = sid_list[:-1]
        sid_list.append(new_version)
        self.SID = self.build_SID(sid_list)

        return new_version

    def get_file_path(self, file, category, release=False):
        outputs = []
        if isinstance(file, list):
            for i in file:
                outputs.append(self._get_files_path(i, category, release))
            return outputs

        outputs.append(self._get_files_path(file, category, release))
        return outputs

    def get_all_file_paths(self, file, category, file_name):
        file_paths = []
        extension = os.path.splitext(file)[-1][1:]
        self.SID = self.conform_file_for_sid(file)
        self.refresh_data()
        versions = self._get_scenes_version()
        for i in versions:
            self.SID = self.sid_replace_core(i)
            if not self.data[i].get(category):
                continue
            if not self.data[i][category].get(file_name):
                continue
            file_path = ""
            if category == CACHES:
                file_path = self.SID_complete_cache_path(geo_type=extension)
            elif category == FLIPBOOKS:
                file_path = self.SID_complete_flipbook_path(format=extension)
            elif category == RENDERS:
                file_path = self.SID_complete_render_path(format=extension)
            elif category == WEDGES:
                file_path = self.SID_complete_daillies_path(session=self.SID_filename)

            file_paths.append(file_path)

        return file_paths

    def get_incr_caches_version_list(self, node, release=False):
        """
        get a list of all caches versions
        Args:
            node: which node to search
            release: tell if release or not

        Returns: a list of all caches versions

        """
        node_name = node.node_name
        node_path = node.node_path
        scenes = self._get_scenes_version()
        if release:
            scenes = [i for i in scenes if self.data[i].get("release")]
            scenes = [i for i in scenes if not isinstance(self.data[i]["release"], bool)]
            scenes = [i for i in scenes if self.data[i]["release"].get(CACHES)]
            scenes = [i for i in scenes if self.data[i]["release"][CACHES].get(node_name)]
            scenes = [i for i in scenes if self.data[i]["release"][CACHES][node_name]["path"] == node_path]
        else:
            scenes = [i for i in scenes if self.data[i].get(CACHES)]
            scenes = [i for i in scenes if self.data[i][CACHES].get(node_name)]
            scenes = [i for i in scenes if self.data[i][CACHES][node_name]["path"] == node_path]

        versions = [SidBdd(i).SID_version for i in scenes]

        return sorted(versions)

    def get_incr_flipbooks_version_list(self, node, release=False):
        """
        get a list of all flipbook versions
        Args:
            node: which node to search
            release: tell if release or not

        Returns: a list of all flipbooks versions

        """
        node_name = node.node_name
        node_path = node.node_path
        scenes = self._get_scenes_version()
        if release:
            scenes = [i for i in scenes if self.data[i].get("release")]
            scenes = [i for i in scenes if not isinstance(self.data[i]["release"], bool)]
            scenes = [i for i in scenes if self.data[i]["release"].get(FLIPBOOKS)]
            scenes = [i for i in scenes if self.data[i]["release"][FLIPBOOKS].get(node_name)]
            scenes = [i for i in scenes if self.data[i]["release"][FLIPBOOKS][node_name]["path"] == node_path]
        else:
            scenes = [i for i in scenes if self.data[i].get(FLIPBOOKS)]
            scenes = [i for i in scenes if self.data[i][FLIPBOOKS].get(node_name)]
            scenes = [i for i in scenes if self.data[i][FLIPBOOKS][node_name]["path"] == node_path]
        versions = [SidBdd(i).SID_version for i in scenes]

        return sorted(versions)

    def get_incr_renders_version_list(self, node, release=False):
        """
        get a list of all renders versions
        Args:
            node: which node to search
            release: tell if release or not

        Returns: a list of all renders versions

        """
        node_name = node.node_name
        node_path = node.node_path
        scenes = self._get_scenes_version()
        if release:
            scenes = [i for i in scenes if self.data[i].get("release")]
            scenes = [i for i in scenes if not isinstance(self.data[i]["release"], bool)]
            scenes = [i for i in scenes if self.data[i]["release"].get(RENDERS)]
            scenes = [i for i in scenes if self.data[i]["release"][RENDERS].get(node_name)]
            scenes = [i for i in scenes if self.data[i]["release"][RENDERS][node_name]["path"] == node_path]
        else:
            scenes = [i for i in scenes if self.data[i].get(RENDERS)]
            scenes = [i for i in scenes if self.data[i][RENDERS].get(node_name)]
            scenes = [i for i in scenes if self.data[i][RENDERS][node_name]["path"] == node_path]
        versions = [SidBdd(i).SID_version for i in scenes]

        return sorted(versions)

    def get_incr_wedgers_version_list(self, node, release=False):
        """
        get a list of all wedgers versions
        Args:
            node: which node to search
            release: tell if release or not

        Returns: a list of all wedgers versions

        """
        node_name = node.node_name
        node_path = node.node_path
        scenes = self._get_scenes_version()
        if release:
            scenes = [i for i in scenes if self.data[i].get("release")]
            scenes = [i for i in scenes if not isinstance(self.data[i]["release"], bool)]
            scenes = [i for i in scenes if self.data[i]["release"].get(WEDGES)]
            scenes = [i for i in scenes if self.data[i]["release"][WEDGES].get(node_name)]
            scenes = [i for i in scenes if self.data[i]["release"][WEDGES][node_name]["path"] == node_path]
        else:
            scenes = [i for i in scenes if self.data[i].get(WEDGES)]
            scenes = [i for i in scenes if self.data[i][WEDGES].get(node_name)]
            scenes = [i for i in scenes if self.data[i][WEDGES][node_name]["path"] == node_path]
        versions = [SidBdd(i).SID_version for i in scenes]

        return sorted(versions)

    def get_scenes_name_list(self, software=None):
        """
        Args:
            software: software used

        Returns: all scenes name which match with project group
        """
        scenes = self._get_scenes()
        name_list = self._get_list_element(software, scenes, "SID_name")

        return name_list

    def get_scenes_task_list(self, software=None):
        """
        Args:
            software: software used

        Returns: all scenes task which match with project group and project name
        """
        scenes = self._get_scenes_task()
        task_list = self._get_list_element(software, scenes, "SID_task")

        return task_list

    def get_scenes_step_list(self, software=None):
        """
        Args:
            software: software used

        Returns: all scenes step which match with project group and project name and project task
        """
        scenes = self._get_scenes_step()
        step_list = self._get_list_element(software, scenes, "SID_step")

        return step_list

    def get_scenes_version_list(self, software=None):
        """
        Args:
            software: software used

        Returns: all scenes versions which match with project group and project name and project task and project step
        """
        scenes = self._get_scenes_version()
        version_list = self._get_list_element(software, scenes, "SID_version")

        return version_list

    def get_scenes_filename_list(self, software=None, release=False):
        """
        Args:
            software: software used

        Returns: all scenes versions which match with project group and project name and project task and project step
        (in file format)
        """
        scenes = self._get_scenes_version(release=release)
        filename_list = self._get_list_element(software, scenes, "conform_sid_for_file()")

        return filename_list

    def get_scenes_filename_list_with_software(self, software=None, release=False):
        """
        Args:
            software: software used

        Returns: all scenes versions which match with project group and project name and project task and project step
        (in file format), and the software used
        """
        liste = []
        scenes = self.get_scenes_filename_list(software=software, release=release)
        for i in scenes:
            soft = ""
            cur_sid = self.conform_file_for_sid(i)
            if self.data.get(cur_sid):
                soft = self.data[cur_sid].get("software")
                data = (soft, i)
                liste.append(data)

        return liste

    def get_commentary(self):
        """

        Returns: the attach commentary

        """
        commentary = self._get_commentary()

        return commentary

    def get_scene_element(self, scene="", release=False):
        """
        get scene datas
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene datas

        """
        datas = {}
        if not self.data.get(scene):
            return datas

        datas = self.data[scene]
        datas = datas if not release else datas["release"]
        return datas

    def get_all_scene_caches(self, scene="", release=False):
        """
        get all scene caches
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene caches datas

        """
        elements = {}
        datas = self.get_scene_element(scene=scene, release=release)
        if not datas.get(CACHES):
            return elements

        elements = datas[CACHES]
        return elements

    def get_scene_cache_node_path(self, scene, release, node):
        """
        get all scene caches node path
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene cache datas paths

        """
        node_path = ""
        datas = self.get_all_scene_caches(scene=scene, release=release)
        if not datas:
            return node_path

        node_path = datas[node]["path"]
        return node_path

    def get_all_scene_flipbooks(self, scene="", release=False):
        """
        get all scene flipbooks
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene flipbooks datas

        """
        elements = {}
        datas = self.get_scene_element(scene=scene, release=release)
        if not datas.get(FLIPBOOKS):
            return elements

        elements = datas[FLIPBOOKS]
        return elements

    def get_scene_flipbook_node_path(self, scene, release, node):
        """
        get all scene flipbooks node path
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene flipbook datas paths

        """
        node_path = ""
        datas = self.get_all_scene_flipbooks(scene=scene, release=release)
        if not datas:
            return node_path

        node_path = datas[node]["path"]
        return node_path

    def get_all_scene_renders(self, scene="", release=False):
        """
        get all scene renders
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene renders datas

        """
        elements = {}
        datas = self.get_scene_element(scene=scene, release=release)
        if not datas.get(RENDERS):
            return elements

        elements = datas[RENDERS]
        return elements

    def get_scene_render_node_path(self, scene, release, node):
        """
        get all scene renders node path
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene renders datas paths

        """
        node_path = ""
        datas = self.get_all_scene_renders(scene=scene, release=release)
        if not datas:
            return node_path

        node_path = datas[node]["path"]
        return node_path

    def get_all_scene_wedges(self, scene="", release=False):
        """
        get all scene wedges
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene wedges datas

        """
        elements = {}
        datas = self.get_scene_element(scene=scene, release=release)
        if not datas.get(WEDGES):
            return elements

        elements = datas[WEDGES]
        return elements

    def get_scene_wedge_node_path(self, scene, release, node):
        """
        get all scene wedges node path
        Args:
            scene: which scene
            release: tell if release or not

        Returns: scene wedges datas paths

        """
        node_path = ""
        datas = self.get_all_scene_wedges(scene=scene, release=release)
        if not datas:
            return node_path

        node_path = datas[node]["path"]
        return node_path

    def get_files(self, release=False):
        """

        Returns: the attach files

        """
        if release:
            files = self._get_files_release()
        else:
            files = self._get_files()
            if isinstance(files.get("release"), dict):
                del files["release"]
            if files.get("commentaries"):
                del files["commentaries"]
            if files.get("software"):
                del files["software"]

        return files

    def get_all_files_category(self, files):
        """
        get all files category
        Args:
            files: which files datas

        Returns: files categories

        """
        liste = []
        if not files:
            return liste

        liste = sorted(list(files.keys()))
        return liste

    def get_all_files_category_childs(self, files, category):
        """
        get all childs category
        Args:
            files: which files datas
            category: which category

        Returns: files categories

        """
        liste = []
        if not files:
            return liste
        if not files.get(category):
            return liste

        liste = sorted(list(files[category].keys()))
        return liste

    def get_child_file_name(self, files, category, child):
        """
        get the file path
        Args:
            files: which files sets
            category: which category
            child: which child

        Returns: file path of the file

        """
        return files[category][child]["file_name"]

    def get_child_node_path(self, files, category, child):
        """
        get the file node_path
        Args:
            files: which files sets
            category: which category
            child: which child

        Returns: node path of the file

        """
        return files[category][child]["path"]

    def modify_project_root(self, path):
        if not path:
            return False
        if not os.path.exists(path):
            return False
        if not os.path.isdir(path):
            return False
        if path == self.data['path']:
            return False

        self.data["path"] = path
        self._save_project(self.data)

    def modify_work_commentaries(self, commentary=None):
        """
        modify work commentaries
        Args:
            commentary: the new commentary

        Returns: True if succeed

        """
        if not commentary:
            return False, ""

        get_work_sid = self.sid_replace_version("000")
        if not self.data.get(get_work_sid):
            msg = "{0} {1}".format(MSG["NO_WORK_SID"], self.SID)
            return False, msg

        self.data[get_work_sid].update({"commentaries": self.commentaries(commentary)})
        self._save_project(self.data)
        return True, ""

    def refresh_data(self):
        """
        refresh database
        Returns:True if succeed

        """
        if os.path.exists(self.project_path):
            self._data = Generic().read_json(data_file=self.project_path)
            return True
        return False


if __name__ == '__main__':
    SID = "myProjects1 | projet1 | fx3d | main | 002"
    SID = "test | test | fx3d | main | 000"
    sid_bdd = SidBdd(SID)
    gna = sid_bdd.get_scenes_filename_list_with_software()
    print(gna)

