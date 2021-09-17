import os

import hou

from rofl_pipeline_tools.rofl_flipbook import Flipbook
from rofl_toolbox.data_base_system.constants import SID_FILE_SEPARATOR
from rofl_pipeline_tools.constants import ROFL_RENDER

class Render(Flipbook):
    def __init__(self, node):
        Flipbook.__init__(self, node)

    def __str__(self):
        if not self.node_type_name == ROFL_RENDER:
            return "The given node isn't a rofl_render"
        return "success loading"

    @property
    def file_format(self):
        return self.node.parm("file_format")

    @property
    def renderer(self):
        return self.node.parm("renderer")

    @property
    def ropnet(self):
        return hou.node(self.node_path + '/ropnet1')

    @property
    def roppath(self):
        return self.node.parm("roppath")

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

            new_file = self.bdd.SID_complete_render_path(format=self.file_format.evalAsString())
            os.rename(os.path.join(folder, i), os.path.join(folder, new_file))

    def _set_arnold(self):
        try:
            render_node = self.ropnet.createNode('arnold')
            self.roppath.set('ropnet1/' + render_node.name())
            render_node.parm('camera').set('`chsop("../../camera")`')
            render_node.parm('ar_picture').set('`chs("../../main_output")`')
            render_node.parm('trange').set(1)
            render_node.parm('f1').setExpression('ch("../../range1")', replace_expression=True)
            render_node.parm('f2').setExpression('ch("../../range2")', replace_expression=True)
            render_node.parm('f3').setExpression('ch("../../range3")', replace_expression=True)
        except:
            print('Arnold is not Installed')

    def _set_bake_texture(self):
        render_node = self.ropnet.createNode('baketexture::3.0')
        self.roppath.set('ropnet1/' + render_node.name())
        render_node.parm('camera').set('`chsop("../../camera")`')
        render_node.parm('vm_uvoutputpicture1').set('`chs("../../main_output")`')
        render_node.parm('trange').set(1)
        render_node.parm('f1').setExpression('ch("../../range1")', replace_expression=True)
        render_node.parm('f2').setExpression('ch("../../range2")', replace_expression=True)
        render_node.parm('f3').setExpression('ch("../../range3")', replace_expression=True)

    def _set_cop(self):
        render_node = self.ropnet.createNode("comp")
        self.roppath.set("ropnet1/" + render_node.name())
        render_node.parm("copoutput").set('`chs("../../main_output")`')
        render_node.parm("trange").set(1)
        render_node.parm('f1').setExpression('ch("../../range1")', replace_expression=True)
        render_node.parm('f2').setExpression('ch("../../range2")', replace_expression=True)
        render_node.parm('f3').setExpression('ch("../../range3")', replace_expression=True)

    def _set_mantra(self):
        render_node = self.ropnet.createNode('ifd')
        self.roppath.set('ropnet1/' + render_node.name())
        render_node.parm('camera').set('`chsop("../../camera")`')
        render_node.parm('vm_picture').set('`chs("../../main_output")`')
        render_node.parm('trange').set(1)
        render_node.parm('f1').setExpression('ch("../../range1")', replace_expression=True)
        render_node.parm('f2').setExpression('ch("../../range2")', replace_expression=True)
        render_node.parm('f3').setExpression('ch("../../range3")', replace_expression=True)

    def _set_redshift(self):
        try:
            render_node = self.ropnet.createNode('Redshift_ROP')
            renderNodeIPR = self.ropnet.createNode('Redshift_IPR')
            renderNodeIPR.move([3, 0])
            self.roppath.set('ropnet1/' + render_node.name())
            render_node.parm('RS_renderCamera').set('`chsop("../../camera")`')
            render_node.parm('RS_outputFileNamePrefix').set('`chs("../../main_output")`')
            render_node.parm('trange').set(1)
            render_node.parm('f1').setExpression('ch("../../range1")', replace_expression=True)
            render_node.parm('f2').setExpression('ch("../../range2")', replace_expression=True)
            render_node.parm('f3').setExpression('ch("../../range3")', replace_expression=True)
        except:
            print('Redshift is not Installed')

    def _set_renderman(self):
        try:
            render_node = self.ropnet.createNode('ris::22')
            self.roppath.set('ropnet1/' + render_node.name())
            render_node.parm('camera').set('`chsop("../../camera")`')
            render_node.parm('ri_display_0').set('`chs("../../main_output")`')
            render_node.parm('trange').set(1)
            render_node.parm('f1').setExpression('ch("../../range1")', replace_expression=True)
            render_node.parm('f2').setExpression('ch("../../range2")', replace_expression=True)
            render_node.parm('f3').setExpression('ch("../../range3")', replace_expression=True)
        except:
            print('Renderman is not Installed')

    def _set_vray(self):
        try:
            render_node = self.ropnet.createNode('vray_renderer')
            self.roppath.set('ropnet1/' + render_node.name())
            render_node.parm('render_camera').set('`chsop("../../camera")`')
            render_node.parm('SettingsOutput_img_file_path').set('`chs("../../main_output")`')
            render_node.parm('trange').set(1)
            render_node.parm('f1').setExpression('ch("../../range1")', replace_expression=True)
            render_node.parm('f2').setExpression('ch("../../range2")', replace_expression=True)
            render_node.parm('f3').setExpression('ch("../../range3")', replace_expression=True)
        except:
            print('vray is not Installed')

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
        versions_list = self.bdd.get_incr_renders_version_list(self, release=search_release)
        for i in versions_list:
            self.menu_item.set("{0} {1}".format(self.menu_item.eval(), i))

        # BUILD MENU FOR "MENU SCRIPT WORKING"
        menuitems = self.menu_item.eval().split()
        menu = ["000", "000"]
        for item in menuitems:
            menu.append(item)
            menu.append(item)

        return menu

    def get_all_renderers(self):
        renderers  = []
        renderers.append("mantra")
        renderers.append("Mantra")
        renderers.append("bake texture")
        renderers.append("bake texture")
        renderers.append("cop")
        renderers.append("COP")
        renderers.append("redshift")
        renderers.append("RedShift")
        renderers.append("arnold")
        renderers.append("Arnold")
        renderers.append("renderman")
        renderers.append("Renderman")
        renderers.append("vray")
        renderers.append("Vray")

        return renderers

    def get_copy_files_infos(self, sid_src_version=None, sid_tgt_version=None, release=False):
        files = {}

        self.bdd.SID = sid_src_version
        self.bdd.SID = self.bdd.sid_slice_to_version()
        self.bdd.SID = self.bdd.sid_replace_version(self.read_version.evalAsString())
        self.bdd.SID = self.bdd.build_SID_name(self.node_name)
        if not self.search_release.eval():
            folder = self.bdd.SID_render_folder_filename(self.file_format.evalAsString())
        else:
            folder = self.bdd.SID_release_render_folder_filename(self.file_format.evalAsString())
        if not os.path.isdir(folder):
            return files

        file_sources = self.get_source_files(folder=folder)
        if not file_sources:
            return files

        for file in file_sources:
            filename = os.path.basename(file)
            self.bdd.SID = self.bdd.conform_file_for_sid(filename)
            self.bdd.SID = self.bdd.sid_replace_core(sid_tgt_version)

            if not release:
                tgt = self.bdd.SID_complete_render_path(format=self.file_format.evalAsString())
            else:
                tgt = self.bdd.SID_release_complete_render_path(format=self.file_format.evalAsString())
            files[filename] = {"src": file, "tgt": tgt}

        return files

    def output(self, script_padding=False, increment=False, release=False, force_sid=None):
        """
        set the output of the render
        Returns: the output file path

        """
        self.build_flipbook_SID(script_padding=script_padding, force_sid=force_sid)
        search_release = self.search_release.eval()
        if release:
            output = self.bdd.SID_release_complete_render_path(format=self.file_format.evalAsString())
            return output

        output = self.bdd.SID_complete_render_path(format=self.file_format.evalAsString())
        if search_release:
            if not increment:
                output = self.bdd.SID_release_complete_render_path(format=self.file_format.evalAsString())
            else:
                output = self.bdd.SID_complete_render_path(format=self.file_format.evalAsString())


        return output

    def on_created(self):
        """
        basic code for node creation

        """
        Flipbook(self.node).on_created_basic()
        self._set_mantra()

    def on_name_changed(self, oldNode):
        """
        basic code for renaming
        Args:
            oldNode: old node name

        """
        folder = Flipbook(self.node).on_name_changed_basic(oldNode)
        self._rename_files_sequence(folder)

    def on_deleted(self):
        """
        basic code for files deletion

        """
        Flipbook(self.node).on_deleted_base()

    def select_renderer(self):
        """
        set connections with user render selection

        """
        selected_renderer = self.renderer.evalAsString()

        for i in self.ropnet.children():
            i.destroy()
            self.roppath.set('')

        if selected_renderer == 'mantra':
            self._set_mantra()
        elif selected_renderer == 'redshift':
            self._set_redshift()
        elif selected_renderer == 'arnold':
            self._set_arnold()
        elif selected_renderer == 'renderman':
            self._set_renderman()
        elif selected_renderer == 'vray':
            self._set_vray()
        elif selected_renderer == "bake texture":
            self._set_bake_texture()
        elif selected_renderer == "cop":
            self._set_cop()

