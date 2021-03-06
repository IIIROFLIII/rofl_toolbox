import os

import hou

from rofl_toolbox.file_manager.widgets.extra_files_manager.api.EFM_generic import EfmGeneric

class EfmHoudini(EfmGeneric):
    def __init__(self):
        EfmGeneric.__init__(self)

    def _append_parm_not_found(self, files):
        """
        append a parm with its file path in the file reference
        certain parms are not recognize by the hou.fileReferences() because of cloning parameters.
        ex: filecache node, the file parameter is not recognize by the fileReferences
        so, just the parameters inside the locked hda are recognize, but it cannot be repathable for the ranch
        so the files can be copied, but no parameters can be repathed on it
        this function check the reference parameters for all parms, and if the parm
        is not already inside the fileReferenced list, we had this missed parameters
        Args:
            files: the files referenced list

        Returns: the updated files referenced list

        """
        # get all the parms found
        all_parms = [file[0] for file in files]
        files_update = list(files)
        for parm, file in files:
            if not parm:
                continue
            # check if the node is inside a locked HDA
            if not parm.node().isInsideLockedHDA():
                continue
            # check if the ref parm is different from the current parm
            ref_parm = parm.getReferencedParm()
            if ref_parm == parm:
                continue
            if not ref_parm:
                continue
            # check if the ref parm is already inside the fileReferenced list
            if ref_parm in all_parms:
                continue

            files_update.append((ref_parm, file))

        files_update = tuple(files_update)
        return files_update

    def get_files(self, selected_items):
        """
        get all the selected files and copy it in the asset folder
        Args:
            selected_items: selected items in EFM UI

        """
        SID = hou.hscriptExpression("$SID")
        self.get_files_generic(SID, selected_items)

    def manage_files(self, extension, parm, file, parm_path, lock_state):
        """
        management of files during the refresh function
        Args:
            extension: extension of the file
            parm: current parm
            file: the file expression in houdini
            parm_path: current parm path (None in this case)
            lock_state: if the parm node is inside locked HDA (no repathing possible if True)

        Returns: True if succeed

        """
        # check if sequence
        frame = hou.frame()
        file_path = parm.evalAtFrame(frame)
        file_path_prev = parm.evalAtFrame(frame-1)
        file_path_next = parm.evalAtFrame(frame+1)
        is_sequence = False if file_path == file_path_prev == file_path_next else True

        if self.manage_files_generic(file_path, extension, is_sequence, file, parm_path, lock_state):
            return True
        return False

    def manage_HDA(self, extension, parm, file, parm_path, lock_state):
        """
        management of HDA during the refresh function
        Args:
            extension: extension of the file
            parm: current parm
            file: the hda file
            parm_path: current parm path (None in this case)
            lock_state: if the parm node is inside locked HDA (True by default)

        Returns: True if succeed

        """
        if not parm and "hda" in extension:
            frames = {file: file}
            self.add_to_database(".HDA", True, file, parm_path, lock_state, frames)
            return True
        return False

    def manage_OTL(self, extension, parm, file, parm_path, lock_state):
        """
        management of HDA during the refresh function
        Args:
            extension: extension of the file
            parm: current parm
            file: the hda file
            parm_path: current parm path (None in this case)
            lock_state: if the parm node is inside locked HDA (True by default)

        Returns: True if succeed

        """
        if not parm and "otl" in extension:
            frames = {file: file}
            self.add_to_database(".OTL", True, file, parm_path, lock_state, frames)
            return True
        return False

    def manage_houdini_scenes(self, extension, file, parm_path, lock_state):
        """
        management of houdini scene during the refresh function
        Args:
            extension: extension of the file
            parm: current parm
            file: the hda file
            parm_path: current parm path (None in this case)
            lock_state: if the parm node is inside locked HDA (True by default)

        Returns: True if succeed

        """
        hou_extensions = ["hip", ".hip", ".hipnc", "hipnc", ".hiplc", "hiplc"]
        if extension == hou_extensions or file == "HIPNAME" or "HIPFILE" in file:
            self.add_to_database("HIP", False, file, parm_path, lock_state)
            return True
        return False

    def manage_rofl_tools(self, parm, file, parm_path, lock_state):
        """
        management of ROFL_TOOLS during the refresh function
        Args:
            parm: current parm
            file: the file expression of the main_output
            parm_path: current parm path
            lock_state: if the parm node is inside locked HDA (no repathing possible if True)

        Returns: True if succeed

        """
        if "rofl" in parm.node().type().name() or "rofl" in parm.node().parent().type().name():
            self.add_to_database("ROFL_TOOLS", False, file.split("\n")[0], parm_path, lock_state)
            return True
        elif "cop2net1/flipbook" in parm_path:
            self.add_to_database("ROFL_TOOLS", False, file.split("\n")[0], parm_path, lock_state)
            return True
        return False

    def refresh_files(self):
        """
        search for all extra files in houdini

        """
        self.datas = {}
        self.SID = hou.hscriptExpression("$SID")

        hou.setUpdateMode(hou.updateMode.Manual)
        files = hou.fileReferences(include_all_refs=True)
        hou.setUpdateMode(hou.updateMode.AutoUpdate)
        files_update = self._append_parm_not_found(files=files)

        for parm, file in files_update:
            extension = os.path.splitext(file)[-1]
            parm_path = parm.path() if parm else "None"
            lock_state = parm.node().isInsideLockedHDA() if parm else True
            parm_eval = parm.eval() if parm else None
            if file.startswith("$HIP/"):
                file = file.replace("$HIP/", hou.hscriptExpression("$HIP") + "/")

            if self.manage_houdini_scenes(extension, file, parm_path, lock_state):
                continue
            if self.manage_HDA(extension, parm, file, parm_path, lock_state):
                continue
            if self.manage_OTL(extension, parm, file, parm_path, lock_state):
                continue
            if self.manage_rofl_tools(parm, file, parm_path, lock_state):
                continue
            if self.manage_already_imported(self.SID, parm_eval, file, parm_path, lock_state):
                continue
            if self.manage_folder(parm_eval, file, parm_path, lock_state):
                continue
            if self.manage_non_ascii(file, parm_path, lock_state):
                continue
            if self.manage_udim(parm_eval, file, parm_path, lock_state):
                continue
            if self.manage_files(extension, parm, file, parm_path, lock_state):
                continue
            self.manage_errors(file, parm_path, lock_state)

    def repathing_parms(self, selected_items):
        """
        repathing all parms according to the items selection
        Args:
            selected_items: selected items in EFM UI

        Returns:

        """
        for item in selected_items:
            if not item.widget.parent_widget.widget.is_allowed:
                continue

            parms = item.widget.parms
            cur_path = item.widget.name
            basename = os.path.basename(cur_path)
            SID = hou.hscriptExpression("$SID")

            for parm in parms:
                parm_path = parm[0]
                is_locked = parm[1]
                if is_locked:
                    continue

                parm_node = hou.parm(parm_path)
                if "rofl" in parm_node.getReferencedParm().node().type().name():
                    continue

                if parm_node.keyframes():
                    parm_node.deleteAllKeyframes()
                parm_node.set(self.get_asset_path(SID, basename))

    def select_parm_node(self, parm_path):
        """
        select the node which contain the given parm path in houdini
        Args:
            parm_path: the parm path to looking for

        """
        if parm_path == "None":
            return False

        hou.parm(parm_path).node().setSelected(True, clear_all_selected=True)


if __name__ == '__main__':
    EFM = EfmHoudini()