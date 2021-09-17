import hou

from rofl_pipeline_tools.rofl_filecache import FileCache
from rofl_pipeline_tools.rofl_filecache_layer import FileCacheLayer
from rofl_pipeline_tools.constants import ROFL_CACHE, ROFL_SEQUENCER

class Sequencer:
    def __init__(self, node):
        self.node = node

    def __str__(self):
        if not self.node.type().name() == ROFL_SEQUENCER:
            return "The given node isn't a rofl_sequencer"
        return "success loading"

    @property
    def control(self):
        return self.node.parm("control")

    @property
    def distribute(self):
        return self.node.parm("distribute")

    @property
    def node_name(self):
        return self.node.name()

    @property
    def node_path(self):
        return self.node.path()

    @property
    def node_type(self):
        return self.node.type()

    @property
    def node_type_name(self):
        return self.node_type.name()

    @property
    def pack_frames(self):
        return self.node.parm("packFrames")

    @property
    def rop_node_path(self):
        return self.node.parm("nodePath")

    @property
    def sim_time(self):
        return self.node.parm('simTime')

    @property
    def slice_count(self):
        return self.node.parm("slicecount")

    @property
    def slice_divs_x(self):
        return self.node.parm("slicedivsx")

    @property
    def slice_divs_y(self):
        return self.node.parm("slicedivsy")

    @property
    def slice_divs_z(self):
        return self.node.parm("slicedivsz")

    @property
    def slice_type(self):
        return self.node.parm("slicetype")

    @property
    def type(self):
        return self.node.parm("type")

    @property
    def verbose_tracker(self):
        return self.node.parm("verbosetracker")

    def check_nodePath(self):
        node = self.rop_node_path.evalAsNode()
        if not node:
            print("Please, set a valid node on nodePath parameter")
            return False
        return node

    def on_created(self):
        """
        code apply on hda creation
        """
        self.node.setColor(hou.Color([0.384, 0.184, 0.329]))

    def on_input_changed(self):
        """
        apply wedger on input changed when the sequencer is inside a rolf_wedger
        """
        if self.node.parent().name() == 'caches':
            wedge_node = self.node.parent().parent()
            wedge_node.hdaModule().on_input_changed(wedge_node)

    def pdg_check_version(self):
        rop_node = FileCache(self.rop_node_path.evalAsNode())
        if not rop_node.read_version.evalAsString() == "000" or rop_node.search_release.eval():
            rop_node.search_release.set(0)
            rop_node.read_version.set("000")
            return False

        layers = rop_node.get_layers()
        for i in layers:
            cur_node = FileCacheLayer(i)
            if not cur_node.pdg_check_version():
                return False
        return True

    def pdg_prepare_sequencer(self, work_item):
        """
        prepare PDG for caching in getting all values needed by the PDG rops (geometry or alembic)
        Returns: a dict with all the attributes needed

        """
        node = self.check_nodePath()
        if not node:
            return False
        if not node.type().name() == ROFL_CACHE:
            return False

        # get rofl filecache node
        filecache = FileCache(node)
        if not filecache.checkpoints():
            return False

        # find wedge suffix
        force_suffix = None
        if filecache.wedge.eval():
            filecache_suffix = filecache.wedge_suffix.rawValue()
            if "@" in filecache_suffix:
                pdg_attrib_name = filecache_suffix[1:-1]
                pdg_attrib_name = pdg_attrib_name.replace("@", "")
                force_suffix = work_item.attribValue(pdg_attrib_name)

        self.sim_time.set("")

        datas = {"string": {},
                 "int": {},
                 "float": {},
                 "filecache": filecache}
        # GET FILECACHE PARAMETERS
        trange = filecache.trange.eval()
        start = filecache.frame_start.eval() if trange else filecache.frame_to_load.eval()
        end = filecache.frame_end.eval() if trange else start
        geoType_name = filecache.geo_type.evalAsString()
        # STRING FILECACHE
        datas["string"].update({"control": self.control.evalAsNode().path() if self.control.evalAsNode() else ""})
        datas["string"].update({"soppath": filecache.rop_geo.inputs()[0].path()})
        datas["string"].update({"output": filecache.output(force_suffix=force_suffix).replace(".0001.", '.$F4.')})
        # INT FILECACHE
        datas["int"].update({"start": int(start)})
        datas["int"].update({"end": int(end)})
        datas["int"].update({"trange": trange})
        datas["int"].update({"geoType": filecache.geo_type.eval()})
        # INT SEQUENCER
        datas["int"].update({"type": self.type.eval()})
        datas["int"].update({"packFrames": self.pack_frames.eval()})
        datas["int"].update({"distribute": self.distribute.eval()})
        datas["int"].update({"slicetype": self.slice_type.eval()})
        datas["int"].update({"slicecount": self.slice_count.eval()})
        datas["int"].update({"verbosetracker": self.verbose_tracker.eval()})
        # FLOAT SEQUENCER
        datas["float"].update({"slicedivsx": self.slice_divs_x.eval()})
        datas["float"].update({"slicedivsy": self.slice_divs_y.eval()})
        datas["float"].update({"slicedivsz": self.slice_divs_z.eval()})
        ###################################
        # GET EXTRA ATTRIBUTES FOR ALEMBIC
        if geoType_name == 'abc':
            datas["float"].update({"shutter1": filecache.shutter1.eval()})
            datas["float"].update({"shutter2": filecache.shutter2.eval()})
            datas["int"].update({"buildFromPath": filecache.build_from_path.eval()})
            datas["int"].update({"sequence": filecache.abc_sequence})
            datas["int"].update({"samples": filecache.samples.eval()})
            datas["int"].update({"packedTransform": filecache.packed_transform.eval()})
            datas["int"].update({"motionblur": filecache.motion_blur.eval()})
            datas["string"].update({"pathAttrib": filecache.path_attrib.eval()})
            datas["string"].update({"pointAttributes": filecache.point_attributes.eval()})
            datas["string"].update({"vertexAttributes": filecache.vertex_attributes.eval()})
            datas["string"].update({"primitiveAttributes": filecache.primitive_attributes.eval()})
            datas["string"].update({"detailAttributes": filecache.detail_attributes.eval()})
            datas["string"].update({"primToDetail": filecache.prim_to_detail.eval()})

        return datas

    def show_explorer(self):
        """
        basic code for opening explorer on file location
        """
        rop_node = self.rop_node_path.evalAsNode()
        if not rop_node:
            return False
        if not rop_node.type().name() == ROFL_CACHE:
            return False

        FileCache(rop_node).show_explorer()

    def show_explorer_hou(self):
        """
        basic code for opening explorer on file location with houdini UI
        """
        rop_node = self.rop_node_path.evalAsNode()
        if not rop_node:
            return False
        if not rop_node.type().name() == ROFL_CACHE:
            return False

        FileCache(rop_node).show_explorer_hou()
