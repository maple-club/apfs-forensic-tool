from PyQt5 import QtWidgets, uic
import os

from .progress import AnalysisProgress

class OpenNewFileUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.analysis_progress = None
        uic.loadUi('gui/design/open_new_file_ui.ui', self)

    def open_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        file_path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            '.',
            'All Files (*)',
            options=options
        )[0]

        if file_path:
            self.filePathEditLine.setText(file_path)
    
    def start_analysis(self):
        file_path = self.filePathEditLine.text()
        if not file_path or not os.path.isfile(file_path):
            QtWidgets.QMessageBox.critical(self, 'Error', 'File Not Selected or Wrong Path!')
        else:
            self.analysis_progress = AnalysisProgress(file_path)
            self.analysis_progress.show()
            self.close()

    def show_event(self, event):
        super().showEvent(event)
        self.filePathEditLine.setText('')
