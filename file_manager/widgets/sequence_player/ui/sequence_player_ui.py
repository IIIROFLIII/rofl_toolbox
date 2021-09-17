import os
import shutil
import random

from PySide2 import QtWidgets, QtCore, QtGui

from rofl_toolbox.file_manager.widgets.settings.api.settings import Settings
from rofl_toolbox.file_manager.constants import SP_SETTINGS, MP4_FOLDER, MSG
from rofl_toolbox.generic_python.python_generic import Generic
from rofl_toolbox.file_manager.widgets.custom_widgets.custom_widgets import ActionButtons, CheckBox
from rofl_toolbox.file_manager.widgets.sequence_player.api.sequence_player import SequencePlayer

# TO DO
# a l occaz les exr meme si ca ca va pas etre simple
# faire des playlists sauvables

class SequenceFrame():
    def __init__(self, image_path=None, image_canvas=None):
        self.image_path = image_path
        self.image_canvas = image_canvas
        self.image = None
        self.size = self.image_canvas.size()

    def get_image(self):
        """
        get picture in QPixmap format and rescaled to the canvas size

        """
        if not self.image:
            if os.path.exists(self.image_path):
                self.image = QtGui.QPixmap(self.image_path)
                self.image = self.image.scaled(self.size, QtCore.Qt.KeepAspectRatio)

        return self.image

class Sequence():
    def __init__(self, image_canvas=None):
        self.frames = {}
        self.image_canvas = image_canvas

    def clear(self):
        self.frames = {}

    def load_files(self, files):
        """
        load all the given files in frames attribute

        """
        self.frames = {}
        for frame in files.keys():
            self.frames.update({frame: SequenceFrame(image_path=files[frame], image_canvas=self.image_canvas)})

    def get_frame(self, frame):
        """
        get the picture path to load according to the frame value
        Args:
            frame: the frame value

        Returns: the file path if succeed

        """
        if len(list(self.frames.keys())) == 1:
            first_key = next(iter(self.frames))
            return self.frames[first_key]

        if self.frames.get(frame):
            return self.frames[frame]
        return False

class little_widget(QtWidgets.QWidget):
    def __init__(self, name="", list_widget=None, item=None):
        super(little_widget, self).__init__()

        self.name = name
        self.list_widget = list_widget
        self.item = item
        self.setup_ui()

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_file_copyer.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()

    def create_widgets(self):
        self.btn_delete = QtWidgets.QPushButton()
        self.lbl_name = QtWidgets.QLabel(self.name[-35:])

    def modify_widgets(self):
        self.btn_delete.setFixedSize(QtCore.QSize(15, 15))
        self.btn_delete.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                     "../../../../resources/icons/remove.png")))

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

    def add_widgets_to_layouts(self):
        self.main_layout.addWidget(self.lbl_name)
        self.main_layout.addStretch()
        self.main_layout.addWidget(self.btn_delete)

    def setup_connections(self):
        self.btn_delete.clicked.connect(self.delete)

    def delete(self):
        items_list = [self.list_widget.item(i) for i in range(self.list_widget.count())]
        if not items_list:
            return False

        self.list_widget.takeItem(self.list_widget.row(self.item))

class WidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, name, list_widget, start, end, files):
        super(WidgetItem, self).__init__()
        self.list_widget = list_widget
        self.name = name
        self.start = start
        self.end = end
        self.files = files
        self.main()

    def main(self):
        self.widget = little_widget(self.name, self.list_widget, self)
        self.setSizeHint(self.widget.sizeHint())
        self.list_widget.addItem(self)
        self.list_widget.setItemWidget(self, self.widget)

class SequencePlayerUi(QtWidgets.QWidget):
    def __init__(self):
        super(SequencePlayerUi, self).__init__()

        self._playback_timer = QtCore.QTimer()
        self._recent_browser_path = ""
        self.setup_ui()
        self._sequence_1 = Sequence(self.image_canvas_1)
        self._sequence_2 = Sequence(self.image_canvas_2)
        self._sequence_3 = Sequence(self.image_canvas_3)
        self._sequence_4 = Sequence(self.image_canvas_4)

        self.load_settings()
        self.set_playback_speed()
        self.installEventFilter(self)
        self.api = SequencePlayer()

    def setup_ui(self):
        # css_file = os.path.join(os.path.dirname(__file__), "../../../../resources/css/style_main.css")
        # with open(css_file, "r") as f:
        #     self.setStyleSheet((f.read()))

        self.create_widgets()
        self.modify_widgets()
        self.set_icons()
        self.create_layouts()
        self.modify_layout()
        self.add_widgets_to_layouts()
        self.setup_connections()
        self.set_tool_tips()

    def create_widgets(self):
        # BTN
        self.btn_hide = ActionButtons("")
        self.btn_mosaic = ActionButtons("")
        self.btn_next = ActionButtons("")
        self.btn_open = ActionButtons("")
        self.btn_pause = ActionButtons("")
        self.btn_play = ActionButtons("")
        self.btn_prev = ActionButtons("")
        self.btn_refresh = ActionButtons("")
        self.btn_sequence = ActionButtons("")

        # CHECKBOX
        self.check_multi_sel = CheckBox(" Multi Selection")

        # FRAME
        self.frame_container = QtWidgets.QFrame()

        # LABEL
        self.lbl_drag_and_drop = QtWidgets.QLabel("or just Drag And Drop a File")
        self.lbl_end = QtWidgets.QLabel(" End ")
        self.lbl_fps = QtWidgets.QLabel(" FPS ")
        self.lbl_frame = QtWidgets.QLabel(" Frame ")
        self.lbl_start = QtWidgets.QLabel(" Start   ")
        self.image_canvas_1 = QtWidgets.QLabel()
        self.image_canvas_2 = QtWidgets.QLabel()
        self.image_canvas_3 = QtWidgets.QLabel()
        self.image_canvas_4 = QtWidgets.QLabel()

        # LIST WIDGET
        self.lw_files = QtWidgets.QListWidget()

        # SLIDER
        self.slider_timeline = QtWidgets.QSlider(QtCore.Qt.Horizontal)

        # SPIN BOX
        self.spn_end = QtWidgets.QSpinBox()
        self.spn_fps = QtWidgets.QSpinBox()
        self.spn_frame = QtWidgets.QSpinBox()
        self.spn_start = QtWidgets.QSpinBox()

    def modify_widgets(self):
        self.setAcceptDrops(True)

        # BTN
        self.btn_hide.setFixedSize(QtCore.QSize(7, self.frame_container.height()))
        self.btn_mosaic.setFixedSize(QtCore.QSize(40, 40))
        self.btn_mosaic.setObjectName("smallSize")
        self.btn_mosaic.setVisible(False)
        self.btn_next.setFixedSize(QtCore.QSize(40, 40))
        self.btn_open.setFixedSize(QtCore.QSize(40, 40))
        self.btn_pause.setFixedSize(QtCore.QSize(50, 50))
        self.btn_pause.setVisible(False)
        self.btn_play.setFixedSize(QtCore.QSize(50, 50))
        self.btn_prev.setFixedSize(QtCore.QSize(40, 40))
        self.btn_refresh.setFixedSize(QtCore.QSize(40, 40))
        self.btn_sequence.setFixedSize(QtCore.QSize(40, 40))
        self.btn_sequence.setObjectName("smallSize")
        self.btn_sequence.setVisible(False)

        # FRAMES
        self.frame_container.setFixedWidth(350)

        # LABEL
        self.lbl_drag_and_drop.setStyleSheet("QLabel{ font-size: 11px; }")
        self.lbl_drag_and_drop.setAlignment(QtCore.Qt.AlignCenter)

        # LIST WIDGET
        self.lw_files.setObjectName("Generic")
        self.lw_files.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)

        # SPIN BOX
        self.spn_end.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spn_end.setFixedSize(QtCore.QSize(60, 25))
        self.spn_end.setAlignment(QtCore.Qt.AlignCenter)

        self.spn_fps.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spn_fps.setFixedSize(QtCore.QSize(60, 25))
        self.spn_fps.setAlignment(QtCore.Qt.AlignCenter)
        self.spn_fps.setValue(Settings().get_fps())
        self.spn_fps.setMaximum(999)

        self.spn_frame.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spn_frame.setFixedSize(QtCore.QSize(60, 25))
        self.spn_frame.setAlignment(QtCore.Qt.AlignCenter)

        self.spn_start.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spn_start.setFixedSize(QtCore.QSize(60, 25))
        self.spn_start.setAlignment(QtCore.Qt.AlignCenter)

        # IMAGE CANVAS
        self.image_canvas_1.setAlignment(QtCore.Qt.AlignCenter)
        self.image_canvas_1.setObjectName("View")

        self.image_canvas_2.setAlignment(QtCore.Qt.AlignCenter)
        self.image_canvas_2.setObjectName("View")
        self.image_canvas_2.setVisible(False)

        self.image_canvas_3.setAlignment(QtCore.Qt.AlignCenter)
        self.image_canvas_3.setObjectName("View")
        self.image_canvas_3.setVisible(False)

        self.image_canvas_4.setAlignment(QtCore.Qt.AlignCenter)
        self.image_canvas_4.setObjectName("View")
        self.image_canvas_4.setVisible(False)

    def set_icons(self):
        # PLAY
        self.btn_play.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                       "../../../../resources/icons/play_white.png")))
        self.btn_play.setIconSize(QtCore.QSize(20, 20))
        # PAUSE
        self.btn_pause.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/pause_white.png")))
        self.btn_pause.setIconSize(QtCore.QSize(20, 20))
        # END
        self.btn_next.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                       "../../../../resources/icons/end_white.png")))
        self.btn_next.setIconSize(QtCore.QSize(15, 15))
        # START
        self.btn_prev.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/start_white.png")))
        self.btn_prev.setIconSize(QtCore.QSize(15, 15))
        # REFRESH
        self.btn_refresh.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/refresh_white.png")))
        self.btn_refresh.setIconSize(QtCore.QSize(30, 30))
        # OPEN
        self.btn_open.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/folder_white.png")))
        self.btn_open.setIconSize(QtCore.QSize(25, 25))
        # SEQUENCE
        self.btn_sequence.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/sequence_white.png")))
        self.btn_sequence.setIconSize(QtCore.QSize(30, 30))
        # TILE
        self.btn_mosaic.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                        "../../../../resources/icons/tile_white.png")))
        self.btn_mosaic.setIconSize(QtCore.QSize(30, 30))

    def create_layouts(self):
        self.main_layout = QtWidgets.QHBoxLayout(self)

        self.timeline_layout = QtWidgets.QHBoxLayout()
        self.playback_layout = QtWidgets.QHBoxLayout()
        self.flipbook_layout = QtWidgets.QVBoxLayout()
        self.files_layout = QtWidgets.QVBoxLayout()
        self.files_btn_layout = QtWidgets.QHBoxLayout()
        self.views_layout = QtWidgets.QGridLayout()
        self.list_options = QtWidgets.QHBoxLayout()

    def modify_layout(self):
        pass

    def add_widgets_to_layouts(self):
        self.timeline_layout.addWidget(self.lbl_start)
        self.timeline_layout.addWidget(self.spn_start)
        self.timeline_layout.addWidget(self.slider_timeline)
        self.timeline_layout.addWidget(self.lbl_end)
        self.timeline_layout.addWidget(self.spn_end)

        self.playback_layout.addWidget(self.lbl_frame)
        self.playback_layout.addWidget(self.spn_frame)
        self.playback_layout.addStretch()
        self.playback_layout.addWidget(self.btn_prev)
        self.playback_layout.addWidget(self.btn_play)
        self.playback_layout.addWidget(self.btn_pause)
        self.playback_layout.addWidget(self.btn_next)
        self.playback_layout.addStretch()
        self.playback_layout.addWidget(self.lbl_fps)
        self.playback_layout.addWidget(self.spn_fps)

        self.views_layout.addWidget(self.image_canvas_1, 0, 0)
        self.views_layout.addWidget(self.image_canvas_2, 0, 1)
        self.views_layout.addWidget(self.image_canvas_3, 1, 0)
        self.views_layout.addWidget(self.image_canvas_4, 1, 1)

        self.flipbook_layout.addLayout(self.views_layout)
        self.flipbook_layout.addLayout(self.timeline_layout)
        self.flipbook_layout.addLayout(self.playback_layout)

        self.files_btn_layout.addWidget(self.btn_open)
        self.files_btn_layout.addWidget(self.lbl_drag_and_drop)

        self.list_options.addWidget(self.check_multi_sel)
        self.list_options.addWidget(self.btn_mosaic)
        self.list_options.addWidget(self.btn_sequence)
        self.list_options.addWidget(self.btn_refresh)

        self.files_layout.addLayout(self.files_btn_layout)
        self.files_layout.addWidget(self.lw_files)
        self.files_layout.addLayout(self.list_options)

        self.frame_container.setLayout(self.files_layout)
        self.main_layout.addWidget(self.frame_container)
        self.main_layout.addWidget(self.btn_hide)
        self.main_layout.addLayout(self.flipbook_layout)

    def setup_connections(self):
        # BTN
        self.btn_hide.clicked.connect(self.show_hide_frame)
        self.btn_mosaic.clicked.connect(self.build_mosaic)
        self.btn_next.clicked.connect(self.frame_to_end)
        self.btn_open.clicked.connect(self.open_file_browser)
        self.btn_pause.clicked.connect(self.toggle_play_pause)
        self.btn_play.clicked.connect(self.toggle_play_pause)
        self.btn_prev.clicked.connect(self.frame_to_start)
        self.btn_refresh.clicked.connect(self.build_single_sequence)
        self.btn_sequence.clicked.connect(self.build_sequence)

        # CHECKBOX
        self.check_multi_sel.clicked.connect(self.multi_selection)

        # LISTWIDGET
        self.lw_files.currentRowChanged.connect(self.build_single_sequence)

        # SPINBOX
        self.spn_frame.valueChanged.connect(lambda: self.set_timeline_frame(self.spn_frame.value()))
        self.spn_fps.valueChanged.connect(self.set_playback_speed)

        # SLIDER
        self.slider_timeline.valueChanged.connect(lambda: self.spn_frame.setValue(self.timeline_frame()))
        self.slider_timeline.valueChanged.connect(self.update_image)
        self.slider_timeline.actionTriggered.connect(self.playback_stop)

        # MISC
        self._playback_timer.timeout.connect(self.frame_increment)

    def set_tool_tips(self):
        self.btn_refresh.setToolTip("Readjust Sequence Size (Keyboard: R)")
        self.btn_mosaic.setToolTip("Readjust Sequence Size (Keyboard: R)")
        self.btn_sequence.setToolTip("Readjust Sequence Size (Keyboard: R)")
        self.btn_hide.setToolTip("Show / Hide Pane Tab (Keyboard: X)")
        self.btn_play.setToolTip("Play Sequence (Keyboard: Space)")
        self.btn_pause.setToolTip("Pause Sequence (Keyboard: Space)")
        self.btn_open.setToolTip("Open File Browser (Keyboard: O)")

    def _add_to_list_widget(self, path):
        """
        add given file to files list
        Args:
            path: the complete path of a file

        Returns: the base name of the path

        """
        basename, files, start, end = Generic().get_all_sequence_files(path)

        lw_item = None
        items = [self.lw_files.item(index).widget.name for index in range(self.lw_files.count())]
        if basename not in items:
            lw_item = WidgetItem(basename, self.lw_files, start, end, files)

        return lw_item

    def _check_if_selected_sources_enough(self, items):
        if not len(items) > 1:
            msg = MSG["NOT_ENOUGH_SOURCES"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False
        return True

    def _clear_loaded_sequences(self):
        self.image_canvas_1.clear()
        self.image_canvas_2.clear()
        self.image_canvas_3.clear()
        self.image_canvas_4.clear()
        self.image_canvas_2.setVisible(False)
        self.image_canvas_3.setVisible(False)
        self.image_canvas_4.setVisible(False)
        self._sequence_1.clear()
        self._sequence_2.clear()
        self._sequence_3.clear()
        self._sequence_4.clear()
        self.frame_to_start()
        # clear timeline background colors
        style = "background: rgba(0, 0, 0, 0);"
        self.slider_timeline.setStyleSheet(style)

    def _settings_read(self):
        """
        load UI previous settings
        Returns: the previous settings after user quit the UI

        """
        datas = Generic().read_json(data_file=SP_SETTINGS)
        return datas

    def _settings_save(self, data):
        """
        save UI current settings
        Args:
            data: the datas to save (which are widgets selection)

        """
        Generic().save_json(data_file=SP_SETTINGS, data=data)

    def add_file(self, path):
        """
        add the given file and launch the play
        Args:
            path: the complete path of a file

        """
        path_valid, path = self.api.check_path(path=path)
        if not path_valid:
            self.nativeParentWidget().statusBar.showMessage(path, 10000)
            return False

        current_item = self._add_to_list_widget(path)
        self.set_list_selection(current_item)

    def build_mosaic(self):
        """
        build a mosaic based on item selection

        """
        self._clear_loaded_sequences()

        # do some checks
        selected_items = self.lw_files.selectedItems()
        if not self._check_if_selected_sources_enough(selected_items):
            return False
        if len(selected_items) > 4:
            msg = MSG["TOO_MUCH_SOURCES"]
            self.nativeParentWidget().statusBar.showMessage(msg, 10000)
            return False

        # display canvas according to the selection number
        for index, item in enumerate(selected_items):
            if not index == 0:
                eval('''self.image_canvas_{0}.setVisible(True)'''.format(index+1))

        # load sequences in image canvas
        start = 10000000
        end = 0
        for index, item in enumerate(selected_items):
            selected_item = selected_items[index]
            start = min(start, selected_item.start)
            end = max(end, selected_item.end)
            files = selected_item.files

            sequence_wrapper = eval('''self._sequence_{0}'''.format(index+1))
            self.load_sequence(sequence_wrapper=sequence_wrapper, files=files, start=start, end=end)

        self.playblack_start()

    def build_single_sequence(self):
        """
        get the selected item and its attributes and launch the sequence

        """
        self._clear_loaded_sequences()

        # do some checks
        if self.check_multi_sel.isChecked():
            return False
        selected_item = self.lw_files.currentItem()
        if not selected_item:
            return False

        # get item attributes
        start = selected_item.start
        end = selected_item.end
        files = selected_item.files

        self.load_sequence(sequence_wrapper=self._sequence_1, files=files, start=start, end=end)
        self.playblack_start()

    def build_sequence(self):
        self._clear_loaded_sequences()

        # do some checks
        selected_items = self.lw_files.selectedItems()
        if not self._check_if_selected_sources_enough(selected_items):
            return False

        # define first random color for timeline background
        alpha = 0.25
        random_hue = random.random()
        random_sat = random.uniform(0.5, 1)
        randdom_val = random.uniform(0.8, 1)
        rgb_1 = Generic().hsv_to_rgb(random_hue, random_sat, randdom_val, alpha)

        # init based attributes
        ramp = ""
        sequence_files = {}
        nb_files = sum([len(list(item.files.keys())) for item in selected_items])

        # build file sequence and timeline background stylesheet
        for index, item in enumerate(selected_items):
            selected_item = item
            files = selected_item.files

            # build the sequence file as a dict
            nb_keys = len(list(sequence_files.keys()))
            for i, frame in enumerate(files):
                sequence_files.update({i+1+nb_keys: files[frame]})

            # do nothing more with the first item
            if index == 0:
                continue

            # define where the sequence start on the timeline
            step = float(nb_keys) / float(nb_files)
            step_1 = step - 0.001
            step_2 = step + 0.001

            # generate a new random color for the timeline background color
            random_hue_2 = random.random()
            random_sat_2 = random.uniform(0.5, 1)
            randdom_val_2 = random.uniform(0.6, 0.8)
            rgb_2 = Generic().hsv_to_rgb(random_hue_2, random_sat_2, randdom_val_2, alpha)

            # complete stylesheet
            ramp += ", stop:{0} rgba{2}, stop:{1} rgba{3}".format(step_1, step_2, rgb_1, rgb_2)

            rgb_1 = rgb_2

        # define start and end of the global sequence
        start = list(sequence_files.keys())[0]
        end = list(sequence_files.keys())[-1]

        # load the entire sequence
        self.load_sequence(sequence_wrapper=self._sequence_1, files=sequence_files, start=start, end=end)

        # apply the background stylesheet
        style = "background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0{0});".format(ramp)
        self.slider_timeline.setStyleSheet(style)

        # launch the playback
        self.playblack_start()

    def frame_decrement(self):
        """
        stop the timeline and play back 1 frame

        """
        self.playback_stop()
        if self.timeline_frame() > self.spn_start.value():
            self.set_timeline_frame(self.timeline_frame() - 1)
        else:
            self.set_timeline_frame(self.spn_end.value())

    def frame_increment(self):
        """
        stop the timeline and ply foreward 1 frame
        Returns:

        """
        if self.timeline_frame() < self.spn_end.value():
            self.set_timeline_frame(self.timeline_frame() + 1)
        else:
            self.set_timeline_frame(self.spn_start.value())

    def frame_to_end(self):
        """
        stop the timeline and go to end of the sequence

        """
        self.playback_stop()
        self.set_timeline_frame(self.spn_end.value())

    def frame_to_start(self):
        """
        stop the timeline and go the start of the sequence

        """
        self.playback_stop()
        self.set_timeline_frame(self.spn_start.value())

    def load_sequence(self, sequence_wrapper=None, files=None, start=None, end=None):
        """
        load all the given sequenced files to be played
        Args:
            files: the list of the files (dict format {frame: path})
            start: start frame
            end: end frame

        """
        self._playback_timer.stop()
        sequence_wrapper.load_files(files=files)
        self.update_ranges(start, end)
        if len(list(files.keys())) == 1:
            self.slider_timeline.setValue(1)

    def load_settings(self):
        """
        load the UI settings

        """
        if not os.path.exists(SP_SETTINGS):
            self._settings_save({"recent_browser_path": self._recent_browser_path})

        data = self._settings_read()
        self._recent_browser_path = data["recent_browser_path"]

    def multi_selection(self):
        self.frame_to_start()
        self._clear_loaded_sequences()
        if self.check_multi_sel.isChecked():
            self.lw_files.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
            self.btn_mosaic.setVisible(True)
            self.btn_sequence.setVisible(True)
            self.btn_refresh.setVisible(False)
        else:
            self.btn_mosaic.setVisible(False)
            self.btn_sequence.setVisible(False)
            self.btn_refresh.setVisible(True)
            self.lw_files.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            selected_items = self.lw_files.selectedItems()
            if not selected_items:
                return False

            self.set_list_selection(selected_items[-1])
            self.build_single_sequence()

    def open_file_browser(self):
        """
        search for a file with os browser

        """
        self.playback_stop()
        # type_filter = "Images (*.exr *.gif *.jpg *.jpeg *.png *.svg *.tga);;All Files (*.*)"
        file_path = QtWidgets.QFileDialog.getOpenFileName(self, 'Open Sequence', self._recent_browser_path)[0]
        if file_path:
            self.add_file(file_path)
            self._recent_browser_path = os.path.dirname(file_path)
            datas = self._settings_read()
            datas["recent_browser_path"] = self._recent_browser_path
            self._settings_save(datas)

    def playblack_start(self):
        """
        start the playback

        """
        self._playback_timer.start()
        self.btn_play.setVisible(False)
        self.btn_pause.setVisible(True)

    def playback_stop(self):
        """
        stop the playback

        """
        self._playback_timer.stop()
        self.btn_play.setVisible(True)
        self.btn_pause.setVisible(False)

    def set_playback_speed(self):
        """
        set playback speed according to the FPS value

        """
        self._playback_timer.setInterval(1000.0 / float(self.spn_fps.value()))

    def set_list_selection(self, item):
        self.lw_files.clearSelection()
        self.lw_files.setCurrentRow(self.lw_files.row(item))

    def set_timeline_frame(self, frame):
        """
        set the good position time on the timeline
        Args:
            frame: which frame to set the timeline

        """
        self.slider_timeline.setValue(frame - self.spn_start.value())

    def show_hide_frame(self):
        if self.frame_container.isHidden():
            self.frame_container.show()
        else:
            self.frame_container.hide()

    def timeline_frame(self):
        """
        get the value of the timeline
        Returns: the value of the timeline

        """
        self.update_image()
        return self.slider_timeline.value() + self.spn_start.value()

    def toggle_play_pause(self):
        """
        play / pause action

        """
        if self._playback_timer.isActive():
            self.playback_stop()
        else:
            if self.spn_end.value() > self.spn_start.value():
                self.playblack_start()

    def update_image(self, position=1):
        """
        set the canvas with the good picture according to the position
        Args:
            position: position to looking fot

        Returns: the displayed picture if succeed

        """
        selected_items = self.lw_files.selectedItems()
        if not selected_items:
            return False

        position += self.spn_start.value()

        for index, item in enumerate(selected_items):
            if index > 3:
                break

            sequence_item = eval('''self._sequence_{0}.get_frame(position)'''.format(index+1))
            if sequence_item:
                image = sequence_item.get_image()

                if image:
                    eval('''self.image_canvas_{0}.setPixmap(image)'''.format(index+1))

    def update_ranges(self, start=None, end=None):
        """
        update all the UI values such as start, end and timeline
        Args:
            start: the start value
            end: the end value

        """
        start = start or self.spn_start.value()
        end = end or self.spn_end.value()
        length = end - start
        self.slider_timeline.setMinimum(0)
        self.slider_timeline.setMaximum(length)
        self.spn_start.setMinimum(start)
        self.spn_start.setMaximum(end)
        self.spn_start.setValue(start)
        self.spn_end.setMinimum(start)
        self.spn_end.setMaximum(end)
        self.spn_end.setValue(end)
        self.spn_frame.setMinimum(start)
        self.spn_frame.setMaximum(end)
        self.spn_frame.setValue(start)

    def eventFilter(self, widget, event):
        """
        apply keyboard event like wheel mouse actions

        """
        if event.type() == QtCore.QEvent.Wheel:
            delta = None
            if 'delta' in dir(event):
                delta = event.delta()
            elif 'angleDelta' in dir(event):
                delta = event.angleDelta()
            if delta and delta > 0:
                self.playback_stop()
                self.frame_decrement()
            else:
                self.playback_stop()
                self.frame_increment()
        elif event.type() == QtCore.QEvent.KeyPress:
            key = event.key()
            if key == QtCore.Qt.Key_X:
                self.show_hide_frame()
            elif key == QtCore.Qt.Key_R:
                if not self.check_multi_sel.isChecked():
                    self.build_single_sequence()
                else:
                    self.build_sequence()
                    self.build_mosaic()
            elif key == QtCore.Qt.Key_Space:
                self.toggle_play_pause()
            elif key == QtCore.Qt.Key_O:
                self.open_file_browser()
        return QtWidgets.QWidget.eventFilter(self, widget, event)

    def dragEnterEvent(self, event):
        event.accept()

    def dragLeaveEvent(self, event):
        pass

    def dropEvent(self, event):
        event.accept()
        for url in event.mimeData().urls():
            self.add_file(path=url.toLocalFile())

    def closeEvent(self, event):
        if os.path.exists(MP4_FOLDER):
            shutil.rmtree(MP4_FOLDER)


if __name__ == '__main__':
    app = QtWidgets.QApplication([])
    fenetre = SequencePlayerUi()
    fenetre.show()
    app.exec_()