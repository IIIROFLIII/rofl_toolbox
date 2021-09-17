import sys

from PySide2 import QtWidgets

from rofl_toolbox.file_manager.main_ui import MainUi

class LaunchApp:
    def __init__(self, window_index=0):
        """
        this class manage the launching of the file manager (FM) according to the software which launch the app
        some applications, like Houdini, needs specific code
        """
        self._software = "Python"
        self._get_launcher()
        self.window_index = window_index
        self.main()

    @property
    def software(self):
        return self._software

    def _get_launcher(self):
        """
        get the software used
        """
        launcher = sys.executable
        if "houdini" in launcher.lower() or "hfs" in launcher:
            self._software = 'Houdini'

    def launch_houdini(self):
        import hou
        fenetre = MainUi(software=self.software)
        fenetre.tab_main.setCurrentIndex(self.window_index)
        fenetre.show()
        hou.session.main = fenetre

    def launch_generic(self):
        app = QtWidgets.QApplication()
        fenetre = MainUi(software=self.software)
        fenetre.tab_main.setCurrentIndex(self.window_index)
        fenetre.show()
        app.exec_()

    def main(self):
        if self.software == "Houdini":
            self.launch_houdini()
        else:
            self.launch_generic()

if __name__ == '__main__':
    LaunchApp()
