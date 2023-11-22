from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from typing import OrderedDict


class MetadataUI(QtWidgets.QWidget):
    def __new__(
            cls,
            data: OrderedDict,
            row_count: int,
            col_count: int = 2
    ):
        if not hasattr(cls, '_instance'):
            cls._instance = super(MetadataUI, cls).__new__(cls)

        return cls._instance

    def __init__(
            self,
            data: OrderedDict,
            row_count: int,
            col_count: int = 2,
    ):
        cls = type(self)
        if not hasattr(cls, '_initialized'):
            super().__init__()
            self.widget: QWidget = uic.loadUi('gui/design/metadata_ui.ui', self)
            self.table_widget: QTableWidget = self.widget.tableWidget
            self.table_widget.setRowCount(row_count)
            self.table_widget.setColumnCount(col_count)
            self.table_widget.setHorizontalHeaderLabels(['key', 'value'])

            idx = 0
            for k, v in data.items():
                self.table_widget.setItem(idx, 0, QTableWidgetItem(k))
                self.table_widget.setItem(idx, 1, QTableWidgetItem(v))
                idx += 1

            self.table_widget.resizeRowsToContents()
            self.table_widget.resizeColumnsToContents()
            self.resize(QSize(self.widget.geometry().width() + 18, self.widget.geometry().height()))
            cls._initialized = True
