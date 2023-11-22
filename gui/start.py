from PyQt5 import QtWidgets, uic

from .opennewfile import OpenNewFileUI
from .openexistfile import OpenExistFileUI

class StartUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui/design/start_ui.ui', self)
        self.new_analysis_ui = None
        self.previous_result_ui = None
        self.initUI()
    
    def initUI(self):
        self.new_analysis_ui = OpenNewFileUI()
        self.previous_result_ui = OpenExistFileUI(method=self.close)
        self.show()

    def open_new_file(self):
        self.new_analysis_ui.show()
    
    def open_existent_file(self):
        self.previous_result_ui.show()
