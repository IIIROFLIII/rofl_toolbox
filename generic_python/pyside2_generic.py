from PySide2 import QtGui

class Pyside2Generic:
    def __init__(self):
        pass

    def center_on_screen(self, widget):
        screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())
        fg = widget.frameGeometry()
        fg.moveCenter(screen.geometry().center())
        widget.move(fg.topLeft())