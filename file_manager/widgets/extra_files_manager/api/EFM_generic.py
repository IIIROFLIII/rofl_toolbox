import os
import re
from glob import glob

from rofl_toolbox.file_manager.widgets.file_copyer.api.file_copyer import FileCopyer
from rofl_toolbox.data_base_system.sid_paths import SidPaths

class DataBase:
    def __init__(self):
        self.datas = {}

    def get_files_infos(self, category, file):
        """
        get all the files infos in the database
        Args:
            category: which category to looking for
            file: which file to looking for

        Returns: files infos

        """
        if not self.datas:
            return False
        if not self.datas.get(category):
            return False
        if not self.datas[category].get(file):
            return False

        return self.datas[category][file]

    def add_extension(self, extension, is_allowed):
        """
        add extension to database
        Args:
            extension: extension name
            is_allowed: extension authorization

        """
        if not self.datas.get(extension):
            self.datas.update({extension: {"is_allowed": is_allowed}})

    def add_file(self, extension, file):
        """
        add file under given category(extension)
        Args:
            extension: extension name
            file: file name

        """
        if not self.datas[extension].get(file):
            self.datas[extension].update({file: {"parm_paths": {},
                                                 "file_sources": {},
                                                 "weight": 0.0}})

    def add_to_database(self, extension, is_allowed, file, parm_path, lock_state, frames=None, is_exist=False):
        """
        add all the datas needed for widget items in the database
        Args:
            extension: extension name
            is_allowed: extension authorization
            file: file name
            parm_path: parm_path
            lock_state: check if parm is repathable
            frames: a list of the files to be copied (files_source)
            is_exist: tell if the datas already exists

        """
        self.add_extension(extension, is_allowed)
        self.add_file(extension, file)

        self.datas[extension][file]["parm_paths"].update({parm_path: {"lock_state": lock_state}})

        if not frames:
            return False
        if is_exist:
            return False

        weight = 0.0
        for frame in frames:
            basename = os.path.basename(frame)
            weight += os.path.getsize(frame)
            self.datas[extension][file]["file_sources"].update({basename: frame})
        self.datas[extension][file]["weight"] = weight

    # def add_to_database(self, extension, is_allowed, file, parm_path, lock_state, frames=None, is_exist=False):
    #     """
    #     add all the datas needed for widget items in the database
    #     Args:
    #         extension: extension name
    #         is_allowed: extension authorization
    #         file: file name
    #         parm_path: parm_path
    #         lock_state: check if parm is repathable
    #         frames: a list of the files to be copied (files_source)
    #         is_exist: tell if the datas already exists
    #
    #     """
    #     self.add_extension(extension, is_allowed)
    #     self.add_file(extension, file)
    #
    #     self.datas[extension][file]["parm_paths"].update({parm_path: {"lock_state": lock_state}})
    #
    #     if not frames:
    #         return False
    #     if is_exist:
    #         return False
    #
    #     weight = 0.0
    #     for key, file_path in frames.items():
    #         basename = os.path.basename(file_path)
    #         weight += os.path.getsize(file_path)
    #         self.datas[extension][file]["file_sources"].update({basename: file_path})
    #     self.datas[extension][file]["weight"] = weight

    def get_all_categories(self):
        """
        get all the categories of the database
        Returns: a list of all the categories

        """
        return sorted(list(self.datas.keys()))

    def get_all_category_files(self, category):
        """
        get all the files contained in the given category of the database
        Args:
            category: which category to looking for

        Returns: a list of the files category

        """
        liste = sorted(list(self.datas[category].keys()))
        liste.remove("is_allowed")
        return liste

    def get_extension_authorization(self, category):
        """
        get if the current extension is allowed to be copied
        Args:
            category: which category to looking for

        Returns: the authorization state

        """
        return self.datas[category]["is_allowed"]

    def get_files_source(self, category, file):
        """
        get the files source of the selected item
        Args:
            category: which category to looking for
            file: which file to looking for

        Returns: the files source of the files

        """
        files_infos = self.get_files_infos(category, file)
        if files_infos and files_infos.get("file_sources"):
            sources = [files_infos["file_sources"][i] for i in list(files_infos["file_sources"].keys())]
            return sorted(sources)
        return []

    def get_folder_path(self, category, file):
        """
        get the folder of the selected item
        Args:
            category: which category to looking for
            file: which file to looking for

        Returns: the folder of the files

        """
        files_infos = self.get_files_infos(category, file)
        if files_infos and files_infos.get("file_sources"):
            file_source = next(iter(files_infos["file_sources"]))
            first_file = files_infos["file_sources"][file_source]
            folder = os.path.dirname(first_file)
            return folder
        return ""

    def get_parms_path(self, category, file):
        """
        get the parms path of the selected item
        Args:
            category: which category to looking for
            file: which file to looking for

        Returns: the parms path of the files

        """
        files_infos = self.get_files_infos(category, file)
        if files_infos and files_infos.get("parm_paths"):
            parms = sorted(list(files_infos["parm_paths"].keys()))
            parm_tuple = [(parm_path, files_infos["parm_paths"][parm_path]["lock_state"]) for parm_path in parms]
            return parm_tuple
        return []

    def get_weight(self, category, file):
        """
        get the weight of the selected item
        Args:
            category: which category to looking for
            file: which file to looking for

        Returns: the weight of the files

        """
        files_infos = self.get_files_infos(category, file)
        if files_infos and files_infos.get("weight"):
            weight = files_infos["weight"]
            return weight
        return 0.0

class EfmGeneric(DataBase):
    def __init__(self):
        DataBase.__init__(self)
        self.files_to_copy = False

    def get_asset_path(self, SID, file_name):
        """
        get SID asset folder path
        Args:
            SID: the current SID
            file_name: file basename

        Returns: the target complete path

        """
        sid_paths = SidPaths(SID)
        return sid_paths.SID_release_asset_complete_path(file_name)

    def get_files_generic(self, SID, selected_items):
        """
        get all the selected files and copy it in the asset folder
        Args:
            selected_items: selected items in EFM UI

        """
        for item in selected_items:
            if not item.widget.is_allowed:
                continue

            files_source = item.widget.files_source
            item_name = item.widget.name
            if not files_source:
                continue

            self.prepare_FileCopyer(SID, item_name, files_source)

    def manage_already_imported(self, SID, parm_eval, file, parm_path, lock_state):
        """
        management of files already imported during the refresh function
        Args:
            SID: current SID
            parm_eval: the expanded string of the parm
            file: the file expression of the main_output
            parm_path: current parm path
            lock_state: if the parm node is inside locked HDA (no repathing possible if True)

        Returns: True if succeed

        """
        if SidPaths(SID).SID_release_asset_folder() in parm_eval:
            self.add_to_database("IS_ALREADY_IMPORTED", False, file, parm_path, lock_state)
            return True
        return False

    def manage_errors(self, file, parm_path, lock_state):
        """
        management files which not corresponding to the other cases
        Args:
            file: the file expression of the main_output
            parm_path: current parm path
            lock_state: if the parm node is inside locked HDA (no repathing possible if True)

        """
        self.add_to_database("ERROR", False, file.split("\n")[0], parm_path, lock_state)

    # def manage_files_generic(self, file_path, extension, is_sequence, file, parm_path, lock_state):
    #     """
    #     management of files during the refresh function
    #     Args:
    #         file_path: the expanded string of the parm
    #         extension: extension of the file
    #         is_sequence: if the string parm is aninmated or not
    #         file: the file expression in houdini
    #         parm_path: current parm path (None in this case)
    #         lock_state: if the parm node is inside locked HDA (no repathing possible if True)
    #
    #     Returns: True if succeed
    #
    #     """
    #     # check file folder
    #     file_folder = os.path.dirname(file_path)
    #     if not os.path.exists(file_folder):
    #         return False
    #
    #     # get files infos
    #     file_name = os.path.basename(file_path)
    #     postfix, prefix = [x[::-1] for x in re.split('[0-9][0-9]+', file_name[::-1], 1)]
    #     extension = os.path.splitext(file_path)[-1] if not extension else extension
    #     extension = ".bgeo" if extension == ".sc" else extension
    #
    #     is_exist = True if self.get_files_infos(extension, file_path) else False
    #     # manage not sequence files
    #     if not is_sequence:
    #         if not is_exist:
    #             if not os.path.exists(file_path):
    #                 return False
    #         frames = [file_path]
    #         self.add_to_database(extension, True, file_path, parm_path, lock_state, frames, is_exist=is_exist)
    #         return True
    #
    #     # manage sequence files
    #     frame_digits = len(file_name) - len(prefix) - len(postfix)
    #     if prefix[-1] == '-':
    #         prefix = prefix[0:-1]
    #     padding = "$F{0}".format(frame_digits)
    #     sequence_path = os.path.join(file_folder, prefix + padding + postfix)
    #
    #     is_exist = True if self.get_files_infos(extension, sequence_path) else False
    #     # don't look for files if the file exist in the database
    #     if not is_exist:
    #         frames = sorted(glob(sequence_path.replace(padding, '-' + '[0-9]' * frame_digits)), reverse=True)
    #         frames += sorted(glob(sequence_path.replace(padding, '[0-9]' * frame_digits)))
    #     else:
    #         frames = self.get_files_source(extension, sequence_path)
    #
    #     # add elements in database
    #     if not frames:
    #         self.add_to_database("NO_FILES_FOUND", False, file, parm_path, lock_state)
    #         return True
    #     self.add_to_database(extension, True, sequence_path, parm_path, lock_state, frames, is_exist=is_exist)
    #     return True

    def manage_files_generic(self, file_path, extension, is_sequence, file, parm_path, lock_state):
        """
        management of files during the refresh function
        Args:
            file_path: the expanded string of the parm
            extension: extension of the file
            is_sequence: if the string parm is aninmated or not
            file: the file expression in houdini
            parm_path: current parm path (None in this case)
            lock_state: if the parm node is inside locked HDA (no repathing possible if True)

        Returns: True if succeed

        """
        # check file folder
        file_folder = os.path.dirname(file_path)
        if not os.path.exists(file_folder):
            return False

        extension = os.path.splitext(file_path)[-1] if not extension else extension
        extension = ".bgeo" if extension == ".sc" else extension

        # get files infos
        file_name = os.path.basename(file_path)
        # manage static frame
        is_exist = True if self.get_files_infos(extension, file_path) else False
        # manage not sequence files
        if not is_sequence:
            if not is_exist:
                if not os.path.exists(file_path):
                    self.add_to_database("NO_FILES_FOUND", False, file_path, parm_path, lock_state)
                    return True
            frames = [file_path]
            self.add_to_database(extension, True, file_path, parm_path, lock_state, frames, is_exist=is_exist)
            return True

        postfix, prefix = [x[::-1] for x in re.split('[0-9][0-9]*', file_name[::-1], 1)]
        # manage sequence files
        frame_digits = len(file_name) - len(prefix) - len(postfix)
        if prefix[-1] == '-':
            prefix = prefix[0:-1]
        padding = "$F{0}".format(frame_digits)
        sequence_path = os.path.join(file_folder, prefix + padding + postfix)

        is_exist = True if self.get_files_infos(extension, sequence_path) else False
        # don't look for files if the file exist in the database
        if not is_exist:
            frames = sorted(glob(sequence_path.replace(padding, '-' + '[0-9]' * frame_digits)), reverse=True)
            frames += sorted(glob(sequence_path.replace(padding, '[0-9]' * frame_digits)))
        else:
            frames = self.get_files_source(extension, sequence_path)

        # add elements in database
        if not frames:
            self.add_to_database("NO_FILES_FOUND", False, file, parm_path, lock_state)
            return True
        self.add_to_database(extension, True, sequence_path, parm_path, lock_state, frames, is_exist=is_exist)
        return True

    def manage_folder(self, parm_eval, file, parm_path, lock_state):
        """
        management of files which is a folder
        Args:
            parm_eval: the expanded string of the parm
            file: the file expression of the main_output
            parm_path: current parm path
            lock_state: if the parm node is inside locked HDA (no repathing possible if True)

        Returns: True if succeed

        """
        if os.path.isdir(parm_eval):
            self.add_to_database("IS_FOLDER", False, file, parm_path, lock_state)
            return True
        return False

    def prepare_FileCopyer(self, SID, item_name, files_source):
        """
        prepare the files copy with the rofl_filecopyer
        Args:
            SID: the current SID
            item_name: the selected item name
            files_source: the files source of the item

        """
        self.SID_FC = FileCopyer()

        for file in files_source:
            src = file
            basename = os.path.basename(src)
            extension = os.path.splitext(src)[-1]
            extension = ".bgeo" if extension == ".sc" else extension
            extension = extension[1:] if extension.startswith(".") else extension

            tgt = self.get_asset_path(SID, basename)
            group = item_name
            self.SID_FC.build_data_files(scene=SID, category=extension, group=group,
                                         filename=basename, src=src, tgt=tgt)

        self.SID_FC.save_json()
        self.files_to_copy = True if self.SID_FC.datas else False