import os

from PySide2 import QtWidgets, QtGui, QtCore

from rofl_toolbox.generic_python.pyside2_generic import Pyside2Generic

class ActionButtons(QtWidgets.QPushButton):
    def __init__(self, text):
        super(ActionButtons, self).__init__(text)

        css_file = os.path.join(os.path.dirname(__file__), "../../../resources/css/style_action_buttons.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))

class CheckBox(QtWidgets.QCheckBox):
    def __init__(self, text):
        super(CheckBox, self).__init__(text)
        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        root = os.path.dirname(root).replace("\\", "/")
        self.setStyleSheet('''
            QCheckBox::indicator:checked
                {
                    image: url( ''' + root + '''/resources/icons/check-mark.png);
                }
            QCheckBox::indicator:unchecked
                {
                    image: url( ''' + root + '''/resources/icons/uncheck-mark.png);
                }
            ''')

class ComboBox(QtWidgets.QComboBox):
    def __init__(self):
        super(ComboBox, self).__init__()

        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        root = os.path.dirname(root).replace("\\", "/")
        self.setStyleSheet('''
            QComboBox::drop-down
                {
                    image: url( ''' + root + '''/resources/icons/open.png);
                }
            ''')

class Label(QtWidgets.QLabel):
    def __init__(self, text):
        super(Label, self).__init__(text)

        css_file = os.path.join(os.path.dirname(__file__), "../../../resources/css/style_label_title.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))

class MessageBox(QtWidgets.QDialog):
    def __init__(self, message="", infos=False, warning=False, question=False):
        super(MessageBox, self).__init__()
        self._valid = None
        self.infos = infos
        self.warning = warning
        self.question = question
        self.message = message

        self.setWindowTitle(self.box_type)
        self.resize(300, 100)
        self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
        self.setWindowIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__),
                                                    "../../../resources/icons/rofl_logo.png")))
        self.setup_ui()

    @property
    def valid(self):
        return self._valid

    @property
    def box_type(self):
        if self.infos:
            return "INFOS"
        elif self.warning:
            return 'WARNING'
        elif self.question:
            return "QUESTION"
        else:
            return None

    def setup_ui(self):
        css_file = os.path.join(os.path.dirname(__file__), "../../../resources/css/style_main.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))
        self.create_widgets()
        self.modify_widgets()
        self.create_layouts()
        self.add_widgets_to_layouts()
        self.setup_connections()
        Pyside2Generic().center_on_screen(self)

    def create_widgets(self):
        self.warning_lbl = QtWidgets.QLabel("{0} : {1}".format(self.box_type, self.message))
        self.ok_btn = ActionButtons("OK")
        self.cancel_btn = ActionButtons("Cancel")
        self.icon_lbl = QtWidgets.QLabel()

    def modify_widgets(self):
        self.ok_btn.setFixedHeight(30)
        self.cancel_btn.setFixedHeight(30)
        if self.box_type == "INFOS":
            self.icon_lbl.setPixmap(QtGui.QIcon("../icons/info.png").pixmap(QtCore.QSize(30, 30)))
        elif self.box_type == "WARNING":
            self.icon_lbl.setPixmap(QtGui.QIcon("../icons/warning.png").pixmap(QtCore.QSize(30, 30)))
        elif self.box_type == "QUESTION":
            self.icon_lbl.setPixmap(QtGui.QIcon("../icons/question.png").pixmap(QtCore.QSize(30, 30)))

    def create_layouts(self):
        self.main_layout = QtWidgets.QVBoxLayout(self)
        self.btn_layout = QtWidgets.QHBoxLayout()
        self.label_layout = QtWidgets.QHBoxLayout()

    def add_widgets_to_layouts(self):
        self.label_layout.addStretch()
        self.label_layout.addWidget(self.icon_lbl)
        self.label_layout.addWidget(self.warning_lbl)
        self.label_layout.addStretch()

        self.btn_layout.addStretch()
        self.btn_layout.addWidget(self.ok_btn)
        self.btn_layout.addWidget(self.cancel_btn)
        self.btn_layout.addStretch()

        self.main_layout.addLayout(self.label_layout)
        self.main_layout.addLayout(self.btn_layout)

    def setup_connections(self):
        self.ok_btn.clicked.connect(self.validate)
        self.cancel_btn.clicked.connect(self.close_widget)

    def validate(self):
        self.close_widget()
        self._valid = True

    def close_widget(self):
        self.close()
        self._valid = False

class SmallButtons(QtWidgets.QPushButton):
    def __init__(self, text):
        super(SmallButtons, self).__init__(text)

        css_file = os.path.join(os.path.dirname(__file__), "../../../resources/css/style_small_buttons.css")
        with open(css_file, "r") as f:
            self.setStyleSheet((f.read()))

class TreeWidget(QtWidgets.QTreeWidget):
    def __init__(self):
        super(TreeWidget, self).__init__()

        root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        root = os.path.dirname(root).replace("\\", "/")
        self.setStyleSheet('''
            QTreeWidget::branch:has-siblings:!adjoins-item
                {
                    border-image: url( ''' + root + '''/resources/icons/vline.png) 0;
                }
                
            QTreeWidget::branch:has-siblings:adjoins-item
                {
                    border-image: url( ''' + root + '''/resources/icons/branch-more.png) 0;
                }
                
            QTreeWidget::branch:!has-children:!has-siblings:adjoins-item
                {
                    border-image: url( ''' + root + '''/resources/icons/branch-end.png) 0;
                }
                
            QTreeWidget::branch:has-children:!has-siblings:closed,
            QTreeWidget::branch:closed:has-children:has-siblings
                {
                    image: url( ''' + root + '''/resources/icons/closed.png);
                }
                
            QTreeWidget::branch:open:has-children:!has-siblings,
            QTreeWidget::branch:open:has-children:has-siblings
                {
                    image: url( ''' + root + '''/resources/icons/open.png);
                }
            ''')

class WidgetItem(QtWidgets.QListWidgetItem):
    def __init__(self, name, list_widget, icon="Folder"):
        super(WidgetItem, self).__init__(name)
        self.list_widget = list_widget
        self.name = name
        self.icon = icon
        self.setTextColor(QtGui.QColor("#fafafa"))

        self.main()

    @property
    def img_folderV(self):
        return QtGui.QIcon(os.path.join(os.path.dirname(__file__), "../../../resources/icons/folderV.png"))

    @property
    def img_houdini(self):
        return QtGui.QIcon(os.path.join(os.path.dirname(__file__), "../../../resources/icons/houdini_logo.png"))

    def main(self):
        icon_file = self.img_folderV
        if self.icon == "Houdini":
            icon_file = self.img_houdini
        self.setIcon(icon_file)
        self.list_widget.addItem(self)