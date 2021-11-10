""" Dialog module for file handling dialogs """
import PySide2.QtCore as QtCore
import PySide2.QtWidgets as QtWidgets


class FileDialog(QtWidgets.QFileDialog):
    """ Custom file dialog, that transfers succesfully selected files to a provided slot """
    def __init__(self, slot, dont_use_native=False, parent=None):
        super().__init__(parent=parent)
        self.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        self.fileSelected.connect(slot)
        if dont_use_native:
            self.setOption(self.DontUseNativeDialog)

    def set_extension(self, extension):
        """ Sets the file extension which the dialog should display """
        self.setDefaultSuffix(extension)
        self.setNameFilter(f'{extension.upper()} file (*.{extension})')

    def showEvent(self, event):
        """ Centers the dialog over the parent window """
        if self.parent():
            parent_window = self.parent().window()
            self.move(parent_window.frameGeometry().topLeft() + \
                      parent_window.rect().center() - \
                      self.rect().center())
        return super().showEvent(event)

    def show_dialog(self, directory, file=None):
        """ Shows the dialog starting in a custom directory, optionally with file proposition """
        self.setDirectory(directory)
        if file:
            self.selectFile(file)
        self.show()


class SaveAsFileDialog(FileDialog):
    """ Custom save as file dialog that reports to a given slot """
    def __init__(self, slot, parent=None):
        super().__init__(slot, dont_use_native=False, parent=parent)
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        self.setWindowTitle('Save as...')


class OpenFileDialog(FileDialog):
    """ Custom save as file dialog that reports to a given slot """
    def __init__(self, slot, parent=None):
        super().__init__(slot, dont_use_native=False, parent=parent)
        self.setAcceptMode(QtWidgets.QFileDialog.AcceptOpen)
        self.setWindowTitle('Open...')


class WidgetDialog(QtWidgets.QDialog):
    """ Standard dialog with buttons """
    def __init__(self, title, main_widget, parent=None):
        super().__init__(parent=parent)
        self.setModal(True)
        self.top_layout = QtWidgets.QVBoxLayout()
        self.button_layout = QtWidgets.QHBoxLayout()
        self.setup_layout(main_widget)
        self.setWindowTitle(title)

    def setup_layout(self, main_widget):
        """ Sets up the dialog layout """
        self.top_layout.addWidget(main_widget)
        self.top_layout.addStretch()
        self.top_layout.addLayout(self.button_layout)
        self.button_layout.addStretch()
        self.setLayout(self.top_layout)

    def add_buttons(self, buttons):
        """ sets up the button box """
        buttons = QtWidgets.QDialogButtonBox(buttons, QtCore.Qt.Horizontal, parent=self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        self.button_layout.addWidget(buttons)


class OkDialog(WidgetDialog):
    """ Widget dialog with Ok button """
    def __init__(self, title, main_widget, parent=None):
        super().__init__(title, main_widget, parent)
        self.add_buttons(QtWidgets.QDialogButtonBox.Ok)


class OkCancelDialog(WidgetDialog):
    """ Widget dialog with Ok and Cancel buttons """
    def __init__(self, title, main_widget, parent=None):
        super().__init__(title, main_widget, parent)
        self.add_buttons(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
