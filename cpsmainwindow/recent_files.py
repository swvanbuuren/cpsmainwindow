""" Tools to track recently opened files and display them in the file menu """

import PySide2.QtWidgets as QtWidgets
import PySide2.QtCore as QtCore


class RecentlyOpenedFiles(QtCore.QObject):
    """ Tracks recently opened files and shows the latest files the file menu """
    filesChanged = QtCore.Signal(list)
    fileTriggered = QtCore.Signal(str)
    defaultOrganization = 'Unknwon organization'
    max_no_files = 10
    max_length = 40
    remain_start = 10
    remain_end = 25

    def __init__(self, menu, anchor, **kwargs):
        super().__init__(parent=kwargs.get('parent'))
        self.actions = list()
        self.filenames = list()
        self.clear_actions = list()
        org_name = kwargs.get('org', self.defaultOrganization)
        app_name = kwargs.get('app')
        self.settings = QtCore.QSettings(org_name, app_name)
        self.create_actions(menu, anchor)
        self.load_files_from_settings()

    def create_actions(self, menu, anchor):
        """ Create all actions and disable visibility """
        for _ in range(self.max_no_files):
            action = QtWidgets.QAction()
            action.setVisible(False)
            action.triggered.connect(self.file_triggered)
            menu.insertAction(anchor, action)
            self.actions.append(action)
        self.create_clear_actions(menu, anchor)
        self.set_no_recent_files_action()

    def create_clear_actions(self, menu, anchor):
        """ Creates the actions the enable to clear all recent files """
        action = QtWidgets.QAction()
        action.setSeparator(True)
        self.clear_actions.append(action)
        menu.insertAction(anchor, action)
        action = QtWidgets.QAction('Clear recent files')
        action.triggered.connect(self.clear_settings)
        menu.insertAction(anchor, action)
        self.clear_actions.append(action)

    def set_no_recent_files_action(self):
        """ Creates a placeholer action, if the first action is not visible and controls the
        visibility of the action to clear recent files """
        first_action = self.actions[0]
        first_action_visible = first_action.isVisible()
        if not first_action_visible:
            first_action.setText('No recent files')
            first_action.setEnabled(False)
            first_action.setVisible(True)
        for action in self.clear_actions:
            action.setVisible(first_action_visible)

    def load_files_from_settings(self):
        """ Loads recently opened files from the application settings """
        files = self.settings.value('recent_files_list', [[]])[0]
        self.load_files(files)

    def clear_settings(self):
        """ Clears all recently opened files from the settings """
        self.settings.remove('recent_files_list')
        self.load_files_from_settings()
        self.update_actions()

    def load_files(self, file_list):
        """
        Loads filenames_list into self.filenames, entries beyond self.max_no_files are ignored
        """
        self.filenames = file_list[:self.max_no_files]
        self.update_actions()

    def enable_action(self, action, filename):
        """ Update a given action """
        text = shorten_name(filename, self.max_length, self.remain_start, self.remain_end)
        action.setText(text)
        action.setStatusTip(f'Open {filename}')
        action.setData(filename)
        action.setEnabled(True)
        action.setVisible(True)

    def update_actions(self):
        """ Enables all actions according to self.filenames, disables others """
        for action, filename in zip(self.actions, self.filenames):
            self.enable_action(action, filename)
        for action in self.actions[len(self.filenames):]:
            action.setVisible(False)
        self.set_no_recent_files_action()
        self.filesChanged.emit(self.filenames)

    @QtCore.Slot(str)
    def add_file(self, filename):
        """ Add a recently opened file, remove duplicates and excess filenames and update actions
        """
        self.filenames.insert(0, filename)
        del self.filenames[self.max_no_files:]
        self.filenames = list(dict.fromkeys(self.filenames))
        self.settings.setValue('recent_files_list', [self.filenames])
        self.update_actions()

    @QtCore.Slot(str)
    def remove_file(self, filename):
        """ Remove a recently opened file, e.g. if the link is not valid anymore """
        self.filenames.remove(filename)
        self.update_actions()

    @QtCore.Slot()
    def file_triggered(self):
        """ If a recently opened file action is triggered, the corresponding filename is emitted """
        sender = self.sender()
        self.fileTriggered.emit(sender.data())


def shorten_name(name, max_length, remain_start, remain_end):
    """ Shortens a name, if it exceeds max_length with remaining parts at start and end """
    if len(name) > max_length:
        return f'{name[:remain_start]} ... {name[-remain_end:]}'
    return name
