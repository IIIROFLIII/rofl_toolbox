import os
import shutil

from rofl_toolbox.file_manager.constants import MSG
from rofl_toolbox.data_base_system.sid_interpreter import sid_generic
from rofl_toolbox.data_base_system.sid_bdd_json import SidBdd
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import MessageBox

class SidSceneManagerCommon(SidBdd):
    def __init__(self, sid=sid_generic()):
        SidBdd.__init__(self, sid)

    def check_matched_SID(self, scene_SID):
        """
        check if the data_base_system given by the UI match with the data_base_system of the scene
        Args:
            scene_SID: the data_base_system of the current scene

        Returns: True if success

        """
        if SidBdd(scene_SID).SID_projectAlias != self.SID_projectAlias:
            return False
        if SidBdd(scene_SID).SID_name != self.SID_name:
            return False
        if SidBdd(scene_SID).SID_task != self.SID_task:
            return False
        if SidBdd(scene_SID).SID_step != self.SID_step:
            return False
        return True

    def _save_in_new_or_existing_scene(self, ui=False, software=None, message_new="", message_exist=""):
        """
        detect the multiple case possible to asks question according to the situation
        Args:
            ui: is direct or is used by increment UI
            software: software used
            message_new: message for save in a new project data_base_system
            message_exist: message for save in an existing project data_base_system

        Returns: True if succeed

        """
        version_list = self.get_scenes_version_list(software=software)
        if not len(version_list):
            msg_box = MessageBox(message=message_new, warning=True)
            msg_box.show()
            msg_box.exec_()
            if not msg_box.valid:
                return False, ""

            if ui:
                return True, ""
            
            # create scene in bdd if the new input doesn't exist
            create_scene, log = self.create_scene(software=software, commentaries="tmp work")
            if not create_scene:
                return False, log
            return True, ""
        else:
            msg_box = MessageBox(message=message_exist, warning=True)
            msg_box.show()
            msg_box.exec_()
            if not msg_box.valid:
                return False, ""

            success, log = self.modify_work_commentaries(commentary="tmp_work")
            if not success:
                return False, log
            return True, ""

    def get_scene_path(self):
        """
        create folder to let the save of the scene
        Returns: the scene path according to the data_base_system
        """
        scene_folder = self.SID_scene_folder()
        if not os.path.isdir(scene_folder):
            os.makedirs(scene_folder)

        scene_path = self.SID_complete_scene_path()
        return scene_path

    def save(self, scene_SID=None, software=None):
        """
        save scene in database directly from the FM and get the scene path
        Args:
            scene_SID: the data_base_system of the current data_base_system
            software: the software used

        Returns: the scene path if succeed

        """
        # case where the current scene is not a pipe scene
        if not scene_SID:
            msg_new = MSG["SAVE_CURRENT_SCENE"]
            msg_exist = MSG["SAVE_EXISTING_SCENE"]
            create_scene, log = self._save_in_new_or_existing_scene(software=software, message_new=msg_new, message_exist=msg_exist)
            if not create_scene:
                return False, log
            return self.get_scene_path(), ""

        # case where the scene is a pipe scene
        match_sid = self.check_matched_SID(scene_SID)
        if not match_sid:
            msg_new = MSG["INCREMENT_SCENE"]
            msg_exist = MSG["SAVE_EXISTING_SCENE"]
            create_scene, log =  self._save_in_new_or_existing_scene(ui=True, software=software, message_new=msg_new, message_exist=msg_exist)
            if not create_scene:
                return False, log

        return True, ""

    def incr_save(self, scene_SID=None, incr=False, software=None, commentary="tmp work"):
        """
        save scene in database with the increment UI and get the scene path
        Args:
            incr: is the save is increment ?
            software: the software used
            commentary: commentary link to the save

        Returns: the scene path if succeed

        """
        version_list = self.get_scenes_version_list()
        # transfer scene in a new project
        if not len(version_list):
            create_scene, log = self.create_scene(software=software, commentaries=commentary)
            if not create_scene:
                return False, log
        # transfer scene in an existing project
        else:
            success, log = self.modify_work_commentaries(commentary=commentary)
            if not success:
                return False, log

        work_path = self.get_scene_path()
        # add scene to bdd if increment
        if incr:
            self.increment_sid()

            if not self.check_matched_SID(scene_SID=scene_SID):
                return work_path, ""

            create_scene, log = self.create_scene(software=software, commentaries=commentary)
            if not create_scene:
                return False, log

        return work_path, ""

    def release_save(self, incr=False, software=None, commentary="tmp work"):
        """
        save scene in database with the increment UI and get the scene path
        Args:
            incr: is the save is increment ?
            software: the software used
            commentary: commentary link to the save

        Returns: the scene path if succeed

        """
        version_list = self.get_scenes_version_list()
        # transfer scene in a new project
        if not len(version_list):
            create_scene, log = self.create_scene(software=software, commentaries=commentary)
            if not create_scene:
                return False, log

        # transfer scene in an existing project
        else:
            success, log = self.modify_work_commentaries(commentary=commentary)
            if not success:
                return False, log

        work_path = self.get_scene_path()
        # add scene to bdd if increment
        if incr:
            self.increment_sid()
            create_scene, log = self.create_scene(software=software, commentaries=commentary, release=True)
            if not create_scene:
                return False, log

        return work_path, ""

    def remove_datas(self, result=None, software=None, type=None):
        """
        remove datas and/or files
        Args:
            result: user choice, must be [DB and Files, DB, None]
            software: software used
            type: type of data to remove (Project, Name, Task...)

        Returns: True if succeed

        """
        if not result:
            return False, ""

        folder = None
        if type == "Project":
            success, log = self.delete_project()
            if not success:
                return False, log
            folder = self.project_root
        elif type == "Name":
            self.delete_all_tasks(software=software)
            folder = self.SID_name_folder()
        elif type == "Task":
            self.delete_all_steps(software=software)
            folder = self.SID_task_folder()
        elif type == "Step":
            self.delete_all_versions(software=software)
            folder = self.SID_scene_step_folder()
        else:
            return False

        if result == "DB":
            return True

        if not os.path.exists(folder):
            return False

        shutil.rmtree(folder)
        return True


if __name__ == '__main__':
    SID = "myProject | test | fx3d | main | 000"
    scene_sid = "myProject | test | render | main | 005"
    sid_actions = SidSceneManagerCommon(sid=SID)

    from PySide2 import QtWidgets
    app = QtWidgets.QApplication()
    save = sid_actions.save(scene_SID=scene_sid)
    print(save)
    app.exec_()


