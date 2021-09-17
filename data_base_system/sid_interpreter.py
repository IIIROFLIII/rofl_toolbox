from rofl_toolbox.data_base_system.constants import SID_SEPARATOR, SID_FILE_SEPARATOR

base = "xxx"
generic_elements = [base, base, base, base, base]

def sid_generic():
    sid_generic = SID_SEPARATOR.join(generic_elements)

    return sid_generic

class SidInterpreter:
    def __init__(self, sid=sid_generic()):
        self.SID = sid

    def __str__(self):
        return self.SID

    @property
    def SID_base(self):
        """

        Returns: the generic value for a data_base_system

        """
        return base

    @property
    def SID_filename(self):
        """

        Returns: the sixth element of a data_base_system (file name)

        """
        return self.SID.split(SID_SEPARATOR)[5]

    @property
    def SID_frame(self):
        """

        Returns: the eight of a data_base_system (file frame)

        """
        return self.SID.split(SID_SEPARATOR)[7]

    @property
    def SID_name(self):
        """

        Returns: the second element of a data_base_system (project name)

        """
        return self.SID.split(SID_SEPARATOR)[1]

    @property
    def SID_projectAlias(self):
        """

        Returns: the first element of a data_base_system (alias project group)

        """
        return self.SID.split(SID_SEPARATOR)[0]

    @property
    def SID_step(self):
        """

        Returns: the fourth element of a data_base_system (project step)

        """
        return self.SID.split(SID_SEPARATOR)[3]

    @property
    def SID_task(self):
        """

        Returns: the third element of a data_base_system (project task)

        """
        return self.SID.split(SID_SEPARATOR)[2]

    @property
    def SID_version(self):
        """

        Returns: the fifth element of a data_base_system (project version)

        """
        return self.SID.split(SID_SEPARATOR)[4]

    @property
    def SID_wedge_suffix(self):
        """

        Returns: the seventh element of a data_base_system (file name)

        """
        return self.SID.split(SID_SEPARATOR)[6]

    @staticmethod
    def build_SID(sid_liste=generic_elements):
        """
        build a data_base_system with a given list
        Args:
            sid_liste: the liste to build the data_base_system with

        Returns: a data_base_system

        """
        return SID_SEPARATOR.join(sid_liste)

    def _build_filename(self, liste):
        """
        set the nomenclature of a file cache, or flipbook or other
        Args:
            liste: the data_base_system liste

        Returns: the filename properly build

        """
        base = liste[:4]
        wedge_suffix = self.SID_wedge_suffix
        if self.SID_wedge_suffix:
            wedge_suffix = "-{0}".format(self.SID_wedge_suffix)

        filename = SID_FILE_SEPARATOR.join(base) + "{0}{1}{2}{0}{3}".format(SID_FILE_SEPARATOR,
                                                                                 self.SID_filename,
                                                                                 wedge_suffix,
                                                                                 self.SID_version)
        if self.SID_frame:
            filename += "." + self.SID_frame

        return filename

    def _build_filename_to_sid(self, liste):
        """
        Args:
            liste: liste of file split with SID_SEPARATOR

        Returns: An updated data_base_system with file informations

        """
        base = liste[:4]
        name, wedge = [liste[4], ""] if len(liste[4].split("-")) != 2 else liste[4].split("-")
        version, frame = liste[5].split(".")[0], liste[5].split(".")[1]
        # frame = frame if frame.isdigit() else ""
        sid = SID_SEPARATOR.join(base) + "{0}{1}{0}{2}{0}{3}{0}{4}".format(SID_SEPARATOR, version, name, wedge, frame)

        return sid

    def build_SID_name(self, name):
        return "{0}{1}{2}".format(self.SID, SID_SEPARATOR, name)

    def build_SID_file(self, name=base, wedge_suffix="", frame="0001"):
        """
        build properly a data_base_system for a file like cache, flipbook or other
        Args:
            name: the name of the file
            wedge_suffix: the variation of the file
            frame: the frame of the file

        Returns: An updated data_base_system

        """
        return self.SID + "{0}{1}{0}{2}{0}{3}".format(SID_SEPARATOR, name, wedge_suffix, frame)

    def conform_file_for_sid(self, file):
        """
        transform a filename in data_base_system format
        Args:
            file: the name of the file

        Returns: a data_base_system

        """
        liste = file.split(SID_FILE_SEPARATOR)
        if len(liste) == 6 and "." in liste[-1]:
            return self._build_filename_to_sid(liste)
        else:
            return SID_SEPARATOR.join(liste)

    def conform_file_to_list(self, file):
        """
        transform a filename in list
        Args:
            file: the name of the file

        Returns: a list

        """
        self.SID = self.conform_file_for_sid(file)
        return self.conform_sid_to_list()

    def conform_sid_for_file(self):
        """
        transform a data_base_system into file format
        Returns: file name

        """
        liste = self.conform_sid_to_list()
        if len(liste) == 8:
            return self._build_filename(liste)
        else:
            return SID_FILE_SEPARATOR.join(self.SID.split(SID_SEPARATOR))

    def conform_sid_to_list(self):
        """
        transform a data_base_system into a list
        Returns: a list

        """
        return self.SID.split(SID_SEPARATOR)

    def sid_replace_core(self, sid=sid_generic()):
        """
        replace the current core sid with the given sid
        Args:
            sid: the new sid

        Returns: a replaced sid with the new sid

        """
        sid_list = self.conform_sid_to_list()
        tgt_list = sid.split(SID_SEPARATOR)
        for i, value in enumerate(sid_list):
            if i < 5:
                sid_list[i] = tgt_list[i]

        return self.build_SID(sid_list)

    def sid_replace_filename(self, new_filename=base):
        """
        replace the filename element in a sid
        Args:
            new_filename: the new name

        Returns: the updated sid

        """
        sid_liste = self.conform_sid_to_list()
        sid_liste[5] = new_filename

        return self.build_SID(sid_liste)

    def sid_replace_frame(self, frame):
        """
        replace the frame element in a sid
        Args:
            frame: the new frame

        Returns: the updated sid

        """
        sid_liste = self.conform_sid_to_list()
        sid_liste[7] = frame

        return self.build_SID(sid_liste)

    def sid_replace_name(self, new_name=base):
        """
        replace the name of the data_base_system by an other value
        Args:
            new_name: the new value

        Returns: a data_base_system with the new name

        """
        sid_list = self.conform_sid_to_list()
        sid_list[1] = new_name

        return self.build_SID(sid_list)

    def sid_replace_project(self, new_project=base):
        """
        replace the project of the data_base_system by an other value
        Args:
            new_project: the new value

        Returns: a data_base_system with the new project

        """
        sid_list = self.conform_sid_to_list()
        sid_list[0] = new_project

        return self.build_SID(sid_list)

    def sid_replace_step(self, new_step=base):
        """
        replace the step of the data_base_system by an other value
        Args:
            new_step: the new value

        Returns: a data_base_system with the new step

        """
        sid_list = self.conform_sid_to_list()
        sid_list[3] = new_step

        return self.build_SID(sid_list)

    def sid_replace_task(self, new_task=base):
        """
        replace the task of the data_base_system by an other value
        Args:
            new_task: the new value

        Returns: a data_base_system with the new task

        """
        sid_list = self.conform_sid_to_list()
        sid_list[2] = new_task

        return self.build_SID(sid_list)

    def sid_replace_version(self, new_version=base):
        """
        replace the version of the data_base_system by an other value
        Args:
            new_version: the new value

        Returns: a data_base_system with the new version

        """
        sid_list = self.conform_sid_to_list()
        sid_list[4] = new_version

        return self.build_SID(sid_list)

    def sid_slice_to_version(self):
        """
        trunc the sid to the version element
        Returns: the truncated sid

        """
        sid_list = self.conform_sid_to_list()[:5]
        return self.build_SID(sid_list)

if __name__ == '__main__':
    sid = "test | test | fx3d | main | 005"
    sid_interp = SidInterpreter(sid)
    sid_interp.SID = sid_interp.build_SID_file(name="tutu", wedge_suffix="001", frame="0002")
    print(sid_interp.SID)
    sid_interp.sid_replace_filename()

