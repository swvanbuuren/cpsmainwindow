""" Classic main window module """
import sys
import os.path as op
import re

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore

import cpsmainwindow.classic_menubar as menubar
import cpsmainwindow.classic_dialogs as dialog


class CpsmainwindowException(Exception):
    """ Root exception for cpsmainwindow """


class CallbackException(CpsmainwindowException):
    """ Raised when a callback malfunctions """


class NoSlotException(CpsmainwindowException):
    """ Raised when a slot is not availabe """


class ClassicMainWindow(QtWidgets.QMainWindow):
    """
    A classic main window implementation in PySide for an empty window offering only an option to
    Qmenus with exit and an about information. It is assumed that this window drives the application
    and all other windows are children of this window.
    """

    def __init__(self, application, app_name, parent=None):
        super().__init__(parent)
        self.application = application
        self.application.setActiveWindow(self)
        self.app_name = app_name
        self.setMenuBar(menubar.ClassicMenuBar(parent=self))
        self.set_statusbar()
        self.resize_window(width=800, height=600)
        self.center_window()

    def resize_window(self, width, height):
        """ Set the window's size """
        self.setMinimumWidth(width)
        self.setMinimumHeight(height)

    def center_window(self):
        """ Centers the window on the screen """
        frame_geometry = self.frameGeometry()
        desktop = self.application.desktop()
        screen = desktop.screenNumber(desktop.cursor().pos())
        center_point = desktop.screenGeometry(screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def add_menu(self, title):
        """ Adds a ClassicMenu to the ClassicMenuBar """
        return self.menuBar().add_menu(title)

    def insert_menu(self, before_tag, title):
        """ Insert a ClassicMenu for menu with before_tag to the ClassicMenuBar """
        return self.menuBar().insert_menu(before_tag, title)

    def menu(self, tag):
        """ Returns a a menu from the menubar """
        return self.menuBar().menus[tag]

    def set_statusbar(self):
        """ Sets the StatusBar with a default message """
        statusbar = DefaultMessageStatusbar('Ready')
        self.setStatusBar(statusbar)

    def run(self, data_file=None):
        """ Shows the classic maindow and start the main event loop """
        self.application.aboutToQuit.connect(self.application.deleteLater)
        self.show()
        self.application.exec_()

    def closeEvent(self, event):
        event.ignore()
        self.request_exit()

    @QtCore.Slot()
    def request_exit(self):
        """ Handles the exit request for the main window """
        self.application.exit()
        sys.exit(0)


class ClassicFileMainWindow(ClassicMainWindow):
    """
    A classic file main window implementation in PySide offering (in addtion to ClassicMainWindow)
    file I/O, a menubar with all the ``classic'' entries, such as open, save (as), recently opened
    files etc.
    """
    def __init__(self, application, org_name=None, app_name=None, parent=None):
        super().__init__(application, app_name, parent)
        self._filename = None
        self.start_path = op.join(op.expanduser('~'), 'Documents')
        self.saveas_dialog = dialog.SaveAsFileDialog(slot=self.save_to_file, parent=self)
        self.open_dialog = dialog.OpenFileDialog(slot=self.load_file, parent=self)
        self.callbacks = {'set_contents': None, 'get_contents': None, 'clear_contents': None}
        self.is_dirty = False
        self.set_filename()
        self.save_action, self.recent_files = self.fill_menubar(org_name, app_name)

    def run_callback(self, callback_type, *args):
        """ Runs a callback function of given type """
        callback = self.callbacks[callback_type]
        if callback:
            return callback(*args)
        raise CallbackException(f'Callback of type {callback_type} is not defined!')

    def set_signals(self, **kwargs):
        """ Connects a given signal to available slot """
        for slot_str, signal in kwargs.items():
            try:
                slot = getattr(self, slot_str)
            except AttributeError as err:
                raise NoSlotException(f'The slot named {slot_str} is not available!') from err
            else:
                signal.connect(slot)

    def fill_menubar(self, org_name, app_name):
        """ Set ClassicMenuBar as the window's MenuBar and connect its signals to ClassicMainWindow
        slots """
        file_menu = self.add_menu('&File')
        file_menu.connect_action(self.show_new_dialog, '&New...', shortcut='Ctrl+N', status_tip='Create a new file ...')
        file_menu.connect_action(self.show_open_dialog, '&Open...', shortcut='Ctrl+O', status_tip='Open an existing file ...')
        save_action = file_menu.connect_action(self.save_file_request, '&Save', shortcut='Ctrl+S', status_tip='Save the current file ...')
        save_action.setDisabled(True)
        file_menu.connect_action(self.show_save_as_dialog, '&Save as...', shortcut='Ctrl+Shift+S', status_tip='Save as another file ...')
        recent_files = file_menu.add_recent_files(self.show_open_dialog, org_name, app_name)
        file_menu.connect_action(self.request_exit, '&Exit', shortcut='Ctrl+Q', status_tip='Exit the application')
        help_menu = self.add_menu('&Help')
        help_menu.connect_action(self.about_qt, '&About Qt', status_tip='Display information about Qt')
        return save_action, recent_files

    def set_filename(self, filename='Untitled'):
        """ Set the current file """
        self._filename = filename
        self.set_window_title()

    def set_window_title(self):
        """ Sets the window title """
        is_dirty_star = '*' if self.is_dirty else ''
        self.setWindowTitle(f'{is_dirty_star}{self._filename} - {self.app_name}')

    def set_file_type(self, extension):
        """ Set the file type for openeing and saving files """
        self.saveas_dialog.set_extension(extension)
        self.open_dialog.set_extension(extension)

    @QtCore.Slot(bool)
    def set_dirty(self, is_dirty=True):
        """ Sets the currently opened file to dirty, i.e. it has unsaved changes or, when is_dirty
        is False, sets the currently opened file as saved, i.e. changes have been saved """
        if self.is_dirty == is_dirty:
            return
        self.is_dirty = is_dirty
        self.set_window_title()
        if self._filename != 'Untitled':
            self.save_action.setDisabled(not is_dirty)

    @QtCore.Slot(str)
    def load_file(self, filename):
        """ Reads a file contents into the text editor """
        try:
            with open(filename, 'r') as file:
                self.run_callback('set_contents', file.read())
        except FileNotFoundError:
            self.recent_files.remove_file(filename)
        else:
            self.set_filename(filename)
            self.set_dirty(is_dirty=False)
            self.recent_files.add_file(filename)

    @QtCore.Slot(str)
    def save_to_file(self, filename):
        """ Saves the text editor's contents to file """
        with open(filename, 'w') as file:
            file.write(self.run_callback('get_contents'))
        self.set_filename(filename)
        self.set_dirty(is_dirty=False)
        self.recent_files.add_file(filename)

    @QtCore.Slot()
    def show_new_dialog(self):
        """ Shows the new dialog """
        if not self.is_dirty or request(self, 'start a new data file'):
            self.run_callback('clear_contents')
            self.set_filename('untitled')
            self.set_dirty(is_dirty=False)

    @QtCore.Slot(str)
    def show_open_dialog(self, filename=None):
        """ Shows the open file dialog """
        message_file = 'another data file'
        if filename:
            message_file = op.basename(filename)
        if not self.is_dirty or request(self, f'open <b>{message_file}</b>'):
            if not filename:
                self.open_dialog.show_dialog(self.start_path)
            else:
                self.load_file(filename)

    @QtCore.Slot()
    def save_file_request(self):
        """ Emits a request to save the current file """
        self.save_to_file(self._filename)

    @QtCore.Slot()
    def show_save_as_dialog(self):
        """ Show the save as dialog """
        self.saveas_dialog.show_dialog(self.start_path, self._filename)

    @QtCore.Slot()
    def request_exit(self):
        """ Handles the exit request for the main window """
        if not self.is_dirty or request(self, f'exit {self.app_name}'):
            super().request_exit()

    @QtCore.Slot()
    def about_qt(self):
        """ Displays a simple message box about Qt. The message includes the version number of Qt
        being used by the application. """
        QtWidgets.QMessageBox.aboutQt(toplevel_widget(self), "About Qt")

    def run(self, data_file=None):
        """ Shows the classic maindow and start the main event loop """
        if data_file is not None:
            self.load_file(data_file)
        super().run(data_file)


def request(parent, core_message):
    """ Shows a message box with a request, including a warning about unsaved
    data """
    window_title = generate_window_title(core_message)
    message = 'Are you sure you want to ' + core_message + '? Unsaved data will be lost!'
    reply = QtWidgets.QMessageBox.question(parent, window_title, message,
                                           QtWidgets.QMessageBox.Ok,
                                           QtWidgets.QMessageBox.Cancel)
    return reply == QtWidgets.QMessageBox.Ok


def warning(parent, core_message):
    """ Shows a message box with a warning/problem """
    window_title = generate_window_title(core_message)
    message = 'There was a problem while ' + core_message + '!'
    QtWidgets.QMessageBox.warning(parent, window_title, message, QtWidgets.QMessageBox.Ok)


def generate_window_title(message, max_title_length=40):
    """ Generate a window title with max. length and without HTML tags """
    message = re.sub('<[^<]+?>', '', message)
    window_title = message[:1].upper() + message[1:] + ' ...'
    if len(window_title) > max_title_length:
        window_title = window_title[:max_title_length]
    return window_title


def toplevel_widget(widget):
    """ Returns the top-level widget (i.e. the widget that has no parent) """
    top_widget = widget
    while top_widget.parentWidget():
        top_widget = top_widget.parentWidget()
    return top_widget


class DefaultMessageStatusbar(QtWidgets.QStatusBar):
    """ QStatusbar with a default message, that is displayed if no other message is currently being
    displayed """
    def __init__(self, default_message, parent=None):
        super().__init__(parent=parent)
        self.default_message = default_message
        self.reset_message()
        self.messageChanged.connect(self.reset_message)

    @QtCore.Slot(str)
    def reset_message(self, message=''):
        """ Sets the default message, if the current message is empty """
        if not message:
            self.showMessage(self.default_message)
