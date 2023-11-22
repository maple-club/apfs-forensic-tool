from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import pyqtSignal, QObject

from analysis.analysis import FileAnalyzer
from apfs.files import *
from apfs.nodes import *
from database.databasemanager import DatabaseManager

import threading
import shutil

class SignalEmitter(QObject):
    finished_signal = pyqtSignal(str)

class AnalysisProgress(QtWidgets.QWidget):
    def __init__(
            self,
            file_path
    ):
        super().__init__()
        uic.loadUi('gui/design/progress_ui.ui', self)
        self.progressLabel.setText(
            '''
            <html>
            <head>
            </head>
            <body>
                <p align="center">Analysis in progress</p>
                <p align="center">Please don\'t close this window.</p>
                <p align="center">Please Wait...</p>
            </body>
            </html>
            '''
        )
        self.save_button: QPushButton = self.saveButton
        self.save_button.hide()

        self.file_path: str = file_path
        self.file_analyzer: FileAnalyzer = None

        self.signal_emitter = SignalEmitter()
        self.signal_emitter.finished_signal.connect(self.finish)

        self.db_manager: DatabaseManager = None

        self.start()

    def start(self):
        threading.Thread(target=self.run).start()

    def run(self):
        self.file_analyzer = FileAnalyzer(self.file_path)
        self.file_analyzer.generate_basic_information()
        self.file_analyzer.analyze()

        self.db_manager = DatabaseManager()
        for key, value in self.file_analyzer.basic_information.items():
            self.db_manager.insert_metadata(key, value)

        apfs_data = self.file_analyzer.apfs_data
        for vi in apfs_data.volume_info:
            nodes = Node(apfs_data, vi)
            files = File(apfs_data, vi, nodes.node_id_offset)
            self.db_manager.insert_analysis_data(files.file_info)

        self.signal_emitter.finished_signal.emit('Complete')

        self.db_manager.close()
        self.file_analyzer.close()

    def finish(self):
        self.progressLabel.setText(
            '''
            <html>
            <head>
            </head>
            <body>
                <p align="center">Analysis complete.</p>
                <p align="center">Save Results...</p>
            </body>
            </html>
            '''
        )
        self.saveButton.show()

        if self.isHidden():
            self.show()

    def save_analysis_file(self):
        options = QtWidgets.QFileDialog.Options()
        file_path, _ = QtWidgets.QFileDialog.getSaveFileName(self, 'Save File', '', 'SQLite3 DB (.db)', options=options)
        if file_path:
            if file_path[-3:] != '.db':
                file_path = file_path + '.db'

            shutil.move(self.db_manager.get_temp_file_path(), file_path)

        self.close()