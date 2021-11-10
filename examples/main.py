""" Standard example with empty classic main window """

import sys
import PySide2.QtWidgets as QtWidgets

import cpsmainwindow as cpm
import cpsmainwindow.classic_dialogs as dialogs


def about_dialog(parent_window):
    """ Returns the about dialog for the Classic Text editor """
    about_widget = QtWidgets.QWidget()
    about_widget.setLayout(QtWidgets.QVBoxLayout())
    about_text = ('<h1>Classic Text editor</h1>'
                  '<p>This is a simple text editor to demonstrate the cpsmaindow package.</p>')
    about_widget.layout().addWidget(QtWidgets.QLabel(about_text))
    return dialogs.OkDialog('About Classic Text Editor', about_widget, parent=parent_window)


def main(data_file=None):
    """ Main function, create a classic text editor and runs it """
    application = QtWidgets.QApplication(sys.argv)
    window = cpm.ClassicFileMainWindow(application, app_name="Classic Text Editor")
    window.set_file_type('txt')
    text_editor = QtWidgets.QTextEdit()
    window.setCentralWidget(text_editor)
    window.callbacks = {'set_contents': text_editor.setPlainText,
                        'get_contents': text_editor.toPlainText,
                        'clear_contents': text_editor.clear}
    text_editor.textChanged.connect(window.set_dirty)

    edit_menu = window.insert_menu(before_tag='help', title='&Edit')
    edit_menu.connect_action(text_editor.undo, '&Undo', shortcut='Ctrl+Z')
    edit_menu.connect_action(text_editor.redo, '&Redo', shortcut='Ctrl+Y')
    edit_menu.addSeparator()
    edit_menu.connect_action(text_editor.copy, '&Copy', shortcut='Ctrl+C')
    edit_menu.connect_action(text_editor.paste, 'Paste', shortcut='Ctrl+V')
    edit_menu.connect_action(text_editor.cut, 'Cut', shortcut='Ctrl+X')

    help_menu = window.menu('help')
    help_menu.connect_action(about_dialog(window).show, 'About Classic Text Editor')

    window.run(data_file)


if __name__ == '__main__':
    main()
