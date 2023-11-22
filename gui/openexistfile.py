from .analysisview import AnalysisView
from PyQt5 import QtWidgets, uic
import os


class OpenExistFileUI(QtWidgets.QWidget):
    def __init__(self, method):
        super().__init__()
        uic.loadUi('gui/design/open_exist_file_ui.ui', self)
        self.parent_close = method

    def open_database_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        db_file_path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            '.',
            'Database files(*.db)',
            options=options
        )[0]

        if db_file_path:
            self.databaseFilePathEditLine.setText(db_file_path)

    def open_apfs_file_dialog(self):
        options = QtWidgets.QFileDialog.Options()
        apfs_file_path = QtWidgets.QFileDialog.getOpenFileName(
            self,
            'Open File',
            '.',
            'All Files (*)',
            options=options
        )[0]

        if apfs_file_path:
            self.apfsFilePathEditLine.setText(apfs_file_path)

    def open_analysis_window(self):
        db_file_path: str = self.databaseFilePathEditLine.text()
        apfs_file_path: str = self.apfsFilePathEditLine.text()

        if not db_file_path:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please select valid database file.')
        elif not apfs_file_path:
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please select valid disk image file.')
        elif not os.path.isfile(db_file_path) or not os.path.isfile(apfs_file_path):
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please select a file(not directory).')
        elif db_file_path[db_file_path.rindex('.'):] != '.db' or apfs_file_path[apfs_file_path.rindex('.'):] != '.vmdk':
            QtWidgets.QMessageBox.critical(self, 'Error', 'Please check file extension.')
        else:
            self.parent_close()
            self.close()
            analysis_view = AnalysisView(
                db_file_path=db_file_path,
                apfs_file_path=apfs_file_path
            )
            analysis_view.show()
