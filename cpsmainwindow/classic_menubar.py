""" Classic main window menubar module """

import PySide2.QtWidgets as QtWidgets

import cpsmainwindow.recent_files as recent_files


class MenuBarException(Exception):
    """ Root exception for the module classic_menubar """


class InvalidArgumentError(MenuBarException):
    """ Invalid arguments supplied """


class ClassicMenu(QtWidgets.QMenu):
    """ Classic file menu """
    def __init__(self, title, parent=None):
        super().__init__(title, parent=parent)
        self.recent_files = None

    def add_action(self, action, before_action=None, is_separated=False):
        """ Appends ot inserts an action tag before before_action's tag """
        if before_action:
            self.insertAction(before_action, action)
        else:
            self.addAction(action)
        if is_separated:
            self.create_separator(visible=action.isVisible(), before_action=action)

    def create_separator(self, visible=True, before_action=None):
        """ Creates a QMenu separator action and adds it to the menu """
        separator = QtWidgets.QAction(parent=self)
        separator.setSeparator(True)
        separator.setVisible(visible)
        self.add_action(separator, before_action=before_action)
        return separator

    def create_action(self, text, before_action=None, is_separated=False, **kwargs):
        """ Creates a QMenu action and adds it to the menu """
        action = QtWidgets.QAction(text, parent=self)
        if 'status_tip' not in kwargs:
            kwargs['status_tip'] = text.replace('&', '')
        self.modify_action(action, text, **kwargs)
        self.add_action(action, before_action=before_action, is_separated=is_separated)
        return action

    @staticmethod
    def modify_action(action, text=None, shortcut=None, status_tip=None, visible=True):
        """ Short hand for modifying properties of a given QAction in the QMenu """
        if text:
            action.setText(text)
        if shortcut:
            action.setShortcut(shortcut)
        if status_tip:
            action.setStatusTip(status_tip)
        action.setVisible(visible)

    def connect_action(self, slot, *args, **kwargs):
        """ Connects a slot with an action's signal triggered and makes it visible. If the action is
        not provided, also offers the possibility to create an action on the fly prior to connecting
        it.

        Supported signatures:
        * slot, action, **kwargs: connects a given action to a slot with optional modifiers in
          **kwargs
        * slot, text, **kwargs: creates a new action using text and **kwargs and connects it to a
          slot
        """
        if not args:
            raise InvalidArgumentError
        if isinstance(args[0], QtWidgets.QAction):
            action = self.modify_action(args[0], **kwargs)
        else:
            action = self.create_action(args[0], **kwargs)
        action.setVisible(True)
        action.triggered.connect(slot)
        return action

    def add_recent_files(self, slot, org_name, app_name):
        """ Adds a recent files actions to the QMenu and connects all actions to slot """
        self.create_separator()
        anchor = self.create_separator()
        self.recent_files = recent_files.RecentlyOpenedFiles(self, anchor, org=org_name,
                                                             app=app_name, parent=self)
        self.recent_files.fileTriggered.connect(slot)
        return self.recent_files


class ClassicMenuBar(QtWidgets.QMenuBar):
    """ A classic menubar """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.menus = {}

    def add_menu(self, title):
        """ Adds a ClassicMenu to the ClassicMenuBar """
        return self.insert_menu(before_tag=None, title=title)

    def insert_menu(self, before_tag, title):
        """ Inserts a ClassicMenu before another ClassicMenuBar """
        before = self.menus.get(before_tag)
        menu = ClassicMenu(title, parent=self)
        if before:
            self.insertMenu(before.menuAction(), menu)
        else:
            self.addMenu(menu)
        self.menus[self.title_to_tag(title)] = menu
        return menu

    @staticmethod
    def title_to_tag(title):
        """ Converts a title into a tag """
        return title.replace('&', '').lower()
