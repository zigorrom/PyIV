import os
import sys
from PyQt4 import QtCore, QtGui

def open_folder_in_explorer(folder):
    print("opening folder")
    request = 'explorer "{0}"'.format(folder)
    print(request)
    os.system(request)

class FolderBrowserButton(QtGui.QPushButton):
    sigFolderSelected = QtCore.pyqtSignal(str)

    def __init__(self, parent = None):
        super().__init__(text="...", parent=parent)
        self._working_directory = ""
        self.setupContextMenu()

    def setupContextMenu(self):
        self.popMenu = QtGui.QMenu(self)
        self.selected_folder_context_menu_item = QtGui.QAction(self)
        self.selected_folder_context_menu_item.triggered.connect(self.on_open_folder_in_explorer)
        self.popMenu.addAction(self.selected_folder_context_menu_item)
        self.popMenu.addSeparator()
        self.setContextMenuPolicy(QtCore.Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.on_folder_browse_button_context_menu)

    @property
    def working_directory(self):
        return self._working_directory

    def __open_dialog(self):
        print("selecting folder")
        abs_path = os.path.abspath(self.working_directory)
        folder_name = QtGui.QFileDialog.getExistingDirectory(
            self,
            caption="Select Working Folder",
            directory=abs_path
        )
        if not folder_name:
            return False
        abs_path = os.path.abspath(folder_name)
        self._working_directory = abs_path
        self.sigFolderSelected.emit(self.working_directory)    
        return True

    def mousePressEvent(self,event):
        if event.button() == QtCore.Qt.LeftButton:
            self.__open_dialog()
            event.accept()

        else:
            QtGui.QPushButton.mousePressEvent(self,event)
        
    def on_folder_browse_button_context_menu(self, point):
        txt = "Not Selected"
        if self.working_directory:
            txt = self.working_directory
        
        self.set_selected_folder_context_menu_item_text(txt)
        self.popMenu.exec_(self.mapToGlobal(point))

    def on_open_folder_in_explorer(self):
        if os.path.exists(self.working_directory):
            open_folder_in_explorer(self.working_directory)

    def set_selected_folder_context_menu_item_text(self,text):
        self.selected_folder_context_menu_item.setText(text)



def folder_changed(folder):
    print(folder)    


if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    wnd = FolderBrowserButton()
    wnd.sigFolderSelected.connect(folder_changed)
    wnd.show()
    app.exec_()