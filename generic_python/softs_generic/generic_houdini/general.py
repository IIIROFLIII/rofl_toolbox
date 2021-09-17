import subprocess
import os
import sys

import hou

class HouGeneral:
    def __init__(self):
        pass

    def get_license_category(self):
        """
        search the extension file according to the licence of the user
        Returns: the file format according the licence of the user
        """
        if hou.isApprentice() == True:
            fileFormat = 'hipnc'
        elif str(hou.licenseCategory()).split('.')[-1] == 'Indie':
            fileFormat = 'hiplc'
        else:
            fileFormat = 'hip'

        return fileFormat

    def load_in_mplay(self, path="", start=1, end=100, inc=1, fps=25, zoom=100, xrow=1, yrow=1):
        """
        load the given sequence(s) in mplay in contact sheet
        enable row and column to view it
        Args:
            path: the sequence(s)
            start: the frame start
            end: the frame end
            inc: the step frame
            fps: frames per second value
            zoom: picture size display factor
            xrow: nb picture in X view (for contact sheets)
            yrow: nb picture in y view (for contact sheets)

        """
        extension = ".exe" if sys.platform == "win32" else ""
        mplay = os.path.join(hou.hscriptExpression('$HFS'), 'bin/mplay{0}'.format(extension))

        currentFrame = format(int(hou.frame()), '04d')
        path = path.replace(currentFrame, '$' + 'F4')
        path = path.replace("$F", "\$F")
        path = path.replace("$T", "\$T")
        path = path.replace("$SF", "\$SF")
        path = os.path.normpath(hou.expandString(path))

        process = '{7} -f {0} {1} {2} -r {3} -z {4} -V {5} {6} -M close -C -p -P loop'.format(start,
                                                                                       end,
                                                                                       inc,
                                                                                       fps,
                                                                                       zoom,
                                                                                       xrow,
                                                                                       yrow,
                                                                                       mplay)

        if sys.platform == "win32":
            subprocess.Popen("{0} {1}".format(process, path), shell=True)
        elif sys.platform == "darwin":
            cmd = [mplay, process]
            paths = path.split(" ; ")
            for i in paths:
                cmd.append(i)
            subprocess.Popen(cmd)
        else:
            cmd = [mplay, process]
            paths = path.split(" ; ")
            for i in paths:
                cmd.append(i)
            subprocess.Popen(cmd)

    def set_env(self, key, value):
        """
        add a variable in the list "Alias and Variables of Houdini"
        Args:
            key: the name of the variable
            value: the value of the variable
        """
        hou.hscript('set -g {0} = "{1}"'.format(key, value))

    def language(self, hscript=False, python=False):
        """
        usefull when setExpression in houdini parameters to give directly python language
        Args:
            hscript: to return hscript language
            python: to return python language

        Returns: the selected language

        """
        lang = {}
        if hscript:
            return hou.exprLanguage.Hscript
        if python:
            return hou.exprLanguage.Python

