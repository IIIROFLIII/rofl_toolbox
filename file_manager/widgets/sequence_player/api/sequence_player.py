import os

from rofl_toolbox.file_manager.constants import MP4_FOLDER, MSG
from rofl_toolbox.generic_python.python_generic import Generic

class SequencePlayer:
    def __init__(self):
        pass

    def check_path(self, path):
        """
        check the given path
        Args:
            path: the path to check

        Returns: the path or result path if mp4

        """
        # check extension
        basename = os.path.basename(path)
        name, cur_extension = os.path.splitext(basename)
        if not cur_extension:
            msg = MSG["NO_EXTENSION"]
            return False, msg

        # check if extension if managed
        extensions = [".jpg", ".png", ".tga", ".tiff", ".mp4"]
        if not cur_extension in extensions:
            msg = MSG["FILE_FORMAT_NOT_MANAGE"]
            return False, msg

        # manage mp4 files (convert to sequence files)
        if cur_extension == ".mp4":
            src = path
            tgt_name = "{0}.%04d{1}".format(name, ".jpg")
            path = os.path.join(MP4_FOLDER, "{0}.0001{1}".format(name, ".jpg"))
            tgt = os.path.join(MP4_FOLDER, tgt_name)
            if not os.path.exists(MP4_FOLDER):
                os.makedirs(MP4_FOLDER)
            Generic().mp4_to_sequence(input=src, output=tgt)
            return True, path

        return True, path