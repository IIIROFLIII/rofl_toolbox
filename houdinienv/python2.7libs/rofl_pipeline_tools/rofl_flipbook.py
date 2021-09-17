import os
import shutil

from PIL import Image, ImageDraw

import hou

from rofl_pipeline_tools.rofl_generic_tools import GenericTools
from rofl_toolbox.data_base_system.constants import SID_FILE_SEPARATOR
from rofl_toolbox.generic_python.softs_generic.generic_houdini.general import HouGeneral
from rofl_toolbox.generic_python.python_generic import Generic
from rofl_pipeline_tools.constants import ROFL_FLIPBOOK

class Flipbook(GenericTools):
    def __init__(self, node):
        GenericTools.__init__(self, node)

    def __str__(self):
        if not self.node_type_name == ROFL_FLIPBOOK:
            return "The given node isn't a rofl_flipbook"
        return "success loading"

    @property
    def backgrounds_folder(self):
        return "{0}/resources/backgrounds".format(hou.hscriptExpression("$ROFL_TOOLS"))

    @property
    def backgrounds_themes(self):
        return os.path.join(self.backgrounds_folder, "themes.json").replace("\\", "/")

    @property
    def camera(self):
        return self.node.parm("camera")

    @property
    def color_bottom(self):
        return self.node.parmTuple("bottomColor")

    @property
    def color_theme(self):
        return self.node.parm("colorThemes")

    @property
    def color_top(self):
        return self.node.parmTuple("topColor")

    @property
    def enable_watermarks(self):
        return self.node.parm("enableWatermarks")

    @property
    def frame_end(self):
        return self.node.parm("range2")

    @property
    def frame_inc(self):
        return self.node.parm("range3")

    @property
    def frame_start(self):
        return self.node.parm("range1")

    @property
    def override_mp4(self):
        return self.node.parm("overrideMp4")

    @property
    def output_mp4(self):
        return self.node.parm("outputMp4")

    def _gradient_color(self, val):
        """
        build a ramp according two colors
        Args:
            val: the pixel line

        Returns: line gradient

        """
        (r1, g1, b1), (r2, g2, b2) = self.color_top.eval(), self.color_bottom.eval()
        r1 *= 255
        g1 *= 255
        b1 *= 255
        r2 *= 255
        g2 *= 255
        b2 *= 255
        v = float(val - 1)
        f = v - int(v)
        return int(r1 + f * (r2 - r1)), int(g1 + f * (g2 - g1)), int(b1 + f * (b2 - b1))

    def _load_color_themes(self):
        """
        load color theme database
        Returns:

        """
        datas = Generic().read_json(data_file=self.backgrounds_themes)
        return datas

    def _rename_files_mp4(self, oldNode):
        """
        rename generated mp4 file when node is rename in houdini
        Args:
            oldNode: the name of the node before renaming
        """
        if self.override_mp4.eval():
            return False

        # DEFINE OLD AND NEW FOLDER
        output_mp4 = self.output_mp4.eval()
        mp4_folder = os.path.dirname(output_mp4)
        mp4_old_folder = os.path.join(os.path.dirname(mp4_folder), oldNode)

        # RENAME FOLDER
        if not os.path.isdir(mp4_old_folder):
            return False
        os.rename(mp4_old_folder, mp4_folder)

        # RENAME FILES
        for i in os.listdir(mp4_folder):
            if len(i.split(SID_FILE_SEPARATOR)) != 6:
                continue

            self.bdd.SID = self.bdd.conform_file_for_sid(i)
            self.bdd.SID = self.bdd.sid_replace_filename(self.node_name)

            new_file = self.bdd.SID_complete_flipbook_mp4_path()
            os.rename(os.path.join(mp4_folder, i), os.path.join(mp4_folder, new_file))

    def _rename_files_sequence(self, folder):
        """
        rename generated files when node is rename in houdini
        Args:
            folder: the name of the folder which contain the files
        """
        if not os.path.exists(folder):
            return False

        for i in os.listdir(folder):
            if len(i.split(SID_FILE_SEPARATOR)) != 6:
                continue

            self.bdd.SID = self.bdd.conform_file_for_sid(i)
            self.bdd.SID = self.bdd.sid_replace_filename(self.node_name)

            new_file = self.bdd.SID_complete_flipbook_path()
            os.rename(os.path.join(folder, i), os.path.join(folder, new_file))

    def _save_themes(self, data):
        """
        save color themes actions
        Args:
            datas: dict to save
        """
        Generic().save_json(data_file=self.backgrounds_themes, data=data)

    def _vert_gradient(self, resx, resy):
        """
        build ramp on PIL image
        Args:
            resx: image size X
            resy: image size Y

        Returns: the gradient ramp into image file

        """
        image = Image.new("RGB", (resx, resy), (0, 0, 0))
        draw = ImageDraw.Draw(image)
        for y in range(0, resx+1):
            f = ((y) / float(resy)) + 1
            color = self._gradient_color(f)
            draw.line([(0, y), (resx, y)], fill=color)

        return image

    def add_theme(self):
        """
        add custom color ramp to database
        """
        name = hou.ui.readInput("Enter Theme Name", ["OK", "Cancel"])[1]
        if not name:
            return False

        datas = self._load_color_themes()
        if name in datas:
            choice = hou.ui.displayMessage("Replace Existing Theme ?", ["Ok", "Cancel"])
            if choice == 1:
                return False

        datas[name] = {"top": self.color_top.eval(),
                       "bottom": self.color_bottom.eval()}

        self._save_themes(datas)
        self.color_theme.set(name)
        self.set_color_themes()

    def build_flipbook_SID(self, script_padding=False, force_sid=None):
        """
        build proper data_base_system according to the flipbook node
        """
        suffix = self.find_wedge_suffix()
        frame = self.find_frame(script_padding=script_padding)
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString()) if not force_sid else force_sid
        self.bdd.SID = self.bdd.build_SID_file(name=self.node_name, wedge_suffix=suffix, frame=frame)

    def delete_blast_folder(self):
        """
        delete temporary folder when watermarks is enabled
        """
        if not self.enable_watermarks.eval():
            return False

        folder = os.path.dirname(self.output_blast())
        shutil.rmtree(folder)

    def find_frame(self, script_padding=False, mp4=False):
        """
        find the current frame
        Returns: frame in str format

        """
        frame = GenericTools(self.node).find_frame(script_padding=script_padding)
        if mp4:
            frame = ""

        return frame

    def find_themes(self):
        """
        get the themes to load in the hda menu parameter
        Returns: a list of the different themes

        """
        datas = self._load_color_themes()
        if datas.get("default"):
            del datas["default"]
        themes = []
        for key, content in datas.items():
            themes.append(key)
            themes.append(key)

        return sorted(themes)

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
        versions_list = self.bdd.get_incr_flipbooks_version_list(self, release=search_release)
        for i in versions_list:
            self.menu_item.set("{0} {1}".format(self.menu_item.eval(), i))

        # BUILD MENU FOR "MENU SCRIPT WORKING"
        menuitems = self.menu_item.eval().split()
        menu = ["000", "000"]
        for item in menuitems:
            menu.append(item)
            menu.append(item)

        return menu

    def get_copy_files_infos(self, sid_src_version=None, sid_tgt_version=None, release=False):
        files = {}

        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_name(self.node_name)
        if not self.search_release.eval():
            folder = self.bdd.SID_flipbook_folder_filename()
        else:
            folder = self.bdd.SID_release_flipbook_folder_filename()
        if not os.path.isdir(folder):
            return files

        # GET FILES
        file_sources = self.get_source_files(folder=folder)
        if not file_sources:
            return files

        for file in file_sources:
            filename = os.path.basename(file)
            self.bdd.SID = self.bdd.conform_file_for_sid(filename)
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)

            if not release:
                tgt = self.bdd.SID_complete_flipbook_path()
            else:
                tgt = self.bdd.SID_release_complete_flipbook_path()
            files[filename] = {"src": file, "tgt": tgt}
        # OVIR SI MAINTENAONT ON PEUT PAS SE SERVIR DU GET FILE SOURCE POUR MP4 MAINTENANT QUE C EST ALLEGER
        # GET MP4
        mp4_sources = self.get_source_files_mp4(sid_src_version=sid_src_version)
        for file in mp4_sources:
            filename = os.path.basename(file)
            self.bdd.SID = self.bdd.conform_file_for_sid(filename)
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)

            if not release:
                tgt = self.bdd.SID_complete_flipbook_mp4_path()
            else:
                tgt = self.bdd.SID_release_complete_flipbook_mp4_path()
            files[filename] = {"src": file, "tgt": tgt}

        return files

    def get_source_files_mp4(self, sid_src_version=None):
        files = {}

        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_name(self.node_name)
        if not self.search_release.eval():
            folder = self.bdd.SID_flipbook_folder_filename(format="mp4")
        else:
            folder = self.bdd.SID_release_flipbook_folder_filename(format="mp4")
        if not os.path.isdir(folder):
            return files

        file_list = os.listdir(folder)
        sid_list = self.bdd.conform_sid_to_list()
        files = [os.path.join(folder, file).replace("\\", "/") for file in file_list
                 if all(item in self.bdd.conform_file_to_list(file) for item in sid_list)]

        return files

    def on_created(self):
        """
        classic on created script + theme database generation if not exists
        """
        self.on_created_basic()
        # if self.node_type_name == ROFL_FLIPBOOK:
        #     self.node.setName("flipbook")

        datas = {"light classic": {"top": (0.4, 0.5, 0.55),
                                   "bottom": (0.75, 0.78, 0.78)},
                 "dark classic": {"top": (0, 0, 0),
                                  "bottom": (0, 0, 0)},
                 "light custom": {"top": (0.56, 0.68, 0.8),
                                  "bottom": (0.0665, 0.08, 0.095)},
                 "dark custom": {"top": (0.365, 0.365, 0.365),
                                 "bottom": (0.06, 0.06, 0.06)},
                 "default": "light classic"
                 }
        if not os.path.exists(self.backgrounds_folder):
            os.makedirs(self.backgrounds_folder)
        if not os.path.exists(self.backgrounds_themes):
            self._save_themes(datas)

        self.set_color_themes(default=True)

    def on_created_basic(self):
        GenericTools(self.node).on_created()

    def on_deleted(self):
        """
        classic on deleted + mp4 deletion
        """
        if not self.on_deleted_base():
            return False

        if self.override_mp4.eval():
            return False

        mp4_folder = os.path.dirname(self.output_mp4.eval())
        if not os.path.isdir(mp4_folder):
            return False

        shutil.rmtree(mp4_folder)

    def on_deleted_base(self):
        """
        apply the on_deleted function in the GenericTools
        it's used by the Wedger to have the deleted function without the mp4 deletion which not exist on wedger

        """
        if not GenericTools(self.node).on_deleted():
            return False
        return True

    def on_name_changed(self, oldNode):
        """
        classic on name changed + mp4 renaming
        Args:
            oldNode: the node name before renaming
        """
        folder = self.on_name_changed_basic(oldNode)
        if os.path.exists(folder):
            self._rename_files_sequence(folder)

        self._rename_files_mp4(oldNode)

    def on_name_changed_basic(self, oldNode):
        """
        classic on name changed + mp4 renaming
        Args:
            oldNode: the node name before renaming
        """
        if not self.check_node_exist():
            return ""

        folder = GenericTools(self.node).on_name_changed(oldNode)
        if not folder:
            return ""

        return folder

    def output_blast(self):
        """
        the output for temporary flipbook if watermarks is enabled
        Returns: path of the output (classic if not watermarks, else temporary path)

        """
        self.build_flipbook_SID()
        output = self.bdd.SID_complete_blast_path() if self.enable_watermarks.eval() else self.bdd.SID_complete_flipbook_path()

        return output

    def output(self, script_padding=False, increment=False, release=False, force_sid=None):
        """
        set the output of the flipbook
        Returns: the output file path

        """
        self.build_flipbook_SID(script_padding=script_padding, force_sid=force_sid)
        search_release = self.search_release.eval()
        if release:
            output = self.bdd.SID_release_complete_flipbook_path()
            return output

        output = self.bdd.SID_complete_flipbook_path()
        if search_release:
            if not increment:
                output = self.bdd.SID_release_complete_flipbook_path()
            else:
                output = self.bdd.SID_complete_flipbook_path()

        return output

    def output_path_mp4(self, increment=False, release=False, force_sid=None):
        """
        set the output of the flipbook mp4
        Returns: the output file path

        """
        suffix = self.find_wedge_suffix()
        frame = self.find_frame(mp4=True)

        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_file(name=self.node_name, wedge_suffix=suffix, frame=frame)

        search_release = self.search_release.eval()
        if release:
            output = self.bdd.SID_release_complete_flipbook_mp4_path()
            return output

        output = self.bdd.SID_complete_flipbook_mp4_path()
        if search_release:
            if not increment:
                output = self.bdd.SID_release_complete_flipbook_mp4_path()
            else:
                output = self.bdd.SID_complete_flipbook_mp4_path()

        return output

    def override_mp4_action(self):
        """
        basic code for output override on hda
        """
        override = self.override_mp4.eval()
        if override:
            self.output_mp4.deleteAllKeyframes()
        else:
            self.output_mp4.revertToDefaults()

    def pdg_init(self):
        """
        start of the ramp building, starting with getting all informations needed to build the ramp
        with _vert_gradient
        Returns: the path of the generated ramp on disk

        """
        cam = self.camera.evalAsNode()
        if not cam:
            return False
        # GET IMAGE SIZE
        override_res = self.node.parm("tres").eval()
        if not override_res:
            resx, resy = cam.parm("resx").eval(), cam.parm("resy").eval()
        else:
            resx, resy = self.node.parm("res1").eval(), self.node.parm("res2").eval()
        # BUILD RAMP
        ramp = self._vert_gradient(resx, resy)
        # SAVE RAMP
        if not os.path.exists(self.backgrounds_folder):
            os.makedirs(self.backgrounds_folder)
        top = "_".join([str(i) for i in self.color_top.eval()])
        bot = "_".join([str(i) for i in self.color_bottom.eval()])
        name = "{0}__{1}__{2}_{3}.jpg".format(top, bot, resx, resy)
        path = os.path.join(self.backgrounds_folder, name)
        ramp.save(path)

        return path

    def pdg_convert_seq_to_mov(self):
        # marche pas si la sequence demarre pas a 1 doit y avoir un argument a rajouter (ptet voir pdg)
        input = self.output(script_padding=True).replace("$F4", "%04d")
        output = self.output_mp4.eval()
        frame_rate = int(hou.hscriptExpression("$FPS"))
        start_frame = int(self.frame_start.eval())
        folder = os.path.dirname(output)
        if not os.path.isdir(folder):
            os.makedirs(folder)

        Generic().sequence_to_mp4(frame_rate=frame_rate, start=start_frame, input=input, output=output)

    def remove_theme(self):
        """
        remove selected theme from database
        """
        choice = hou.ui.displayMessage("Delete Selected Theme ?", ["OK", "Cancel"])
        if choice == 1:
            return False

        datas = self._load_color_themes()
        selected_theme = self.color_theme.evalAsString()
        del datas[selected_theme]
        self._save_themes(datas)
        self.color_theme.set(0)
        self.set_color_themes()

    def set_color_themes(self, default=False):
        """
        apply color to parameters according to the database

        """
        datas = self._load_color_themes()
        if not datas:
            return False

        selected_theme = datas["default"] if default else self.color_theme.evalAsString()
        self.color_top.set(datas[selected_theme]["top"])
        self.color_bottom.set(datas[selected_theme]["bottom"])
        self.color_theme.set(selected_theme)

        datas["default"] = selected_theme
        self._save_themes(datas)

    def show_explorer_hou(self):
        """
        custom show explorer with houdini ui,
        on windows, this let loading multiple file sequence to mplay
        doesn't work ye on linux et osx

        """
        sequences = GenericTools(self.node).show_explorer_hou()
        nb_sequences = (len(sequences.split(';')))
        if sequences:
            self.view_img_seq(sequences, nb_sequences)

    def view_img_seq(self, sequences="", nb_sequences=1):
        """
        get all the infos to load the according sequence to mplay
        Args:
            sequences: path of the sequence
            nb_sequences: number of sequence to load (only works on windows for now)

        """
        path = sequences if sequences else self.main_output.eval()
        if not path:
            print("No sequence files found")
            return False

        start = self.frame_start.eval()
        end = self.frame_end.eval()
        inc = self.frame_inc.eval()
        fps = hou.hscriptExpression('$FPS')
        xrow = nb_sequences if nb_sequences == 2 else min(4, int(round(nb_sequences / 2)))
        yrow = nb_sequences / 2 if nb_sequences == 2 else min(4, int(round(nb_sequences / 2)))

        HouGeneral().load_in_mplay(path=path, start=start, end=end, inc=inc, fps=fps, xrow=xrow, yrow=yrow)