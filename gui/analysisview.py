import sqlite3
import os

from typing import OrderedDict, List, BinaryIO, Dict

from PyQt5 import QtWidgets, uic
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

from math import ceil

from analysis.analysis import FileAnalyzer
from apfs.apfs import Apfs
from .metadataview import MetadataUI
from database.databasemanager import DatabaseManager


class AnalysisView(QtWidgets.QMainWindow):
    BUFSIZ = 2048
    INF = 9999

    def __init__(
            self,
            apfs_file_path: str,
            db_file_path: str
    ):
        super().__init__()
        self.apfs_file_path: str = apfs_file_path
        self.apfs: Apfs = None
        self.apfs_file: BinaryIO = None
        self.db_file_path: str = db_file_path
        self.db_file_name: str = self.db_file_path[
            self.db_file_path.rindex('/') + 1:self.db_file_path.rindex('.')
        ]  # database_file_path.split('\\')[-1][:-2]
        self._conn: sqlite3.Connection = None
        self._cursor: sqlite3.Cursor = None

        self.main_window: QMainWindow = uic.loadUi('gui/design/analysis_view_ui.ui', self)
        self.tree_widget: QTreeWidget = self.main_window.treeWidget
        self.table_widget: QTableWidget = self.main_window.tableWidget
        self.hex_area: QScrollArea = self.main_window.hexArea
        self.spin_box: QSpinBox = self.main_window.spinBox
        self.spin_box.setMinimum(-self.INF)
        self.spin_box.setMaximum(self.INF)

        self.metadata_widget: QWidget = None

        # 1.
        # 파일 열기
        self.open_file()

        # 2.
        # FileAnalyzer를 통한 기본정보 생성
        file_analyzer = FileAnalyzer(apfs_file_path)
        QMessageBox.information(self, 'Information', 'Close this window to start integrity check.')
        hash_info: Dict[str, str] = file_analyzer.get_hash()
        self.metadata: OrderedDict[str, str] = self.__read_metadata()
        for key, value in hash_info.items():
            if self.metadata[key] != value:
                QMessageBox.critical(self, 'Alert', 'Disk integrity check failed')
                exit(-1)
        del file_analyzer
        del hash_info

        QMessageBox.information(self, 'Information', 'Integrity check complete.\nClose this window to view the analysis results')

        # 3.
        # 메타데이터 정보를 읽어와서 UI를 생성한다
        # ...는 initUI() 내부에서 한다.
        # 4.
        # QTreeWidget 가져와서 따따따따 붙이기
        # treeWidget, tableWidget, hexArea를 setting한다.
        # ...도 initUI() 내부에서 한다.
        self.initUI()

    def open_file(self):
        self.apfs_file = open(self.apfs_file_path, 'rb')
        self.apfs = Apfs(f=self.apfs_file)
        self._conn = sqlite3.connect(self.db_file_path, isolation_level=None)
        self._cursor = self._conn.cursor()

    def initUI(self):
        self.__metadataUI()
        self.__treeUI()
        self.__menuBarUI()

    ################################################ tree
    def __treeUI(self):
        self.tree_widget = self.main_window.treeWidget
        self.__add_items_to_tree(
            tree_widget=self.tree_widget,
        )
        self.tree_widget.itemClicked.connect(self.__tableUI)

    def __add_items_to_tree(
            self,
            tree_widget: QtWidgets.QTreeWidget,
    ):
        parent = QTreeWidgetItem(tree_widget)
        parent.setText(0, DatabaseManager.APFS_TABLE_NAME)
        child = QTreeWidgetItem(parent)
        child.setText(0, DatabaseManager.APFS_TABLE_NAME)
        # table_name=self.apfs_file_name,
        self.__add_child_to_tree(
            table_name=DatabaseManager.APFS_TABLE_NAME,
            parent=child,
            parent_id='0x1'
        )

    def __add_child_to_tree(
            self,
            table_name: str,
            parent: QTreeWidgetItem,
            parent_id: str
    ):
        query = \
            f'''
            SELECT *
            FROM {table_name}
            WHERE parent_folder_id=\'{parent_id}\'
            AND group_permission/4096=4
            '''
        self._cursor.execute(query)
        result = self._cursor.fetchall()
        for r in result:
            child = QTreeWidgetItem(parent)
            child.setText(0, r[12])  # col_idx=12 -> name
            self.__add_child_to_tree(
                table_name=table_name,
                parent=child,
                parent_id=r[1]  # col_idx=1 -> parent_idx
            )

    ################################################ table
    def __tableUI(self):
        selected_file = self.main_window.treeWidget.currentItem()
        if selected_file.text(0) == 'apfs':
            return

        tmp = selected_file
        while tmp.parent() and tmp.parent().text(0) != 'apfs':
            tmp = tmp.parent()
        query = \
            f'''
            SELECT file_id
            FROM {DatabaseManager.APFS_TABLE_NAME}
            WHERE name = \'{selected_file.text(0)}\'
            '''
        self._cursor.execute(query)

        try:
            parent_id = self._cursor.fetchone()[0]
        except:
            return

        query = \
            f'''
            SELECT name, file_size, group_permission, last_written_date \
            FROM apfs \
            WHERE parent_folder_id = '{parent_id}' \
            AND block_count NOT NULL
            '''

        self._cursor.execute(query)
        result = self._cursor.fetchall()
        row_count = len(result)

        # Setting 
        self.table_widget.itemClicked.connect(self.__hexUI)
        self.table_widget.setRowCount(row_count)
        self.table_widget.setColumnCount(4)
        self.table_widget.setHorizontalHeaderLabels(['name', 'file size', 'category', 'last modified date'])
        self.table_widget.setColumnWidth(0, 250)
        self.table_widget.setColumnWidth(1, 100)
        self.table_widget.setColumnWidth(2, 100)
        self.table_widget.setColumnWidth(3, 300)
        for i in range(row_count):
            name, file_size, group_permission, last_written_date = result[i]
            self.table_widget.setItem(i, 0, QTableWidgetItem(name))
            self.table_widget.setItem(i, 1, QTableWidgetItem(file_size))

            if int(group_permission) // 0x1000 == 8:
                self.table_widget.setItem(i, 2, QTableWidgetItem('File'))
            else:
                self.table_widget.setItem(i, 2, QTableWidgetItem('Directory'))

            self.table_widget.setItem(i, 3, QTableWidgetItem(last_written_date))


    def __hexUI(self):
        # row_idx = self.table_widget.currentRow()
        row = self.table_widget.currentIndex().row()
        selected_name = self.table_widget.item(row, 0).text()
        # selected_name = self.table_widget.selectedItems()[0].text()
        query = \
            f'''
            SELECT file_size, block_count, group_permission
            FROM apfs
            WHERE name = \'{selected_name}\'
            '''
        self._cursor.execute(query)
        file_size, block_count, group_permission = self._cursor.fetchone()

        msg: List[str] = []
        if int(group_permission)//0x1000 == 4:
            # msg.append('This is a directory.')
            msg = 'This is a directory.'
            label = QLabel()
            label.setText(msg)
            label.setFont(QFont('Courier New', 8, QFont.Normal, True))
            label.adjustSize()
            self.hex_area.setWidget(label)
        elif not block_count:
            QMessageBox.critical(self, 'Alert', 'Unreadable file.')
            return

        # Setting spinBox
        self.file_size = int(file_size)
        self.block_count = int(block_count)
        self.spin_box.setMinimum(1)
        self.spin_box.setMaximum(ceil(self.file_size/self.BUFSIZ))

        # self.__get_first_hex_data(block_count=block_count)
        #self.spin_box.editingFinished.connect(
        #    lambda: self.__get_hex_data(m=ceil(file_size/self.BUFSIZ), block_count=block_count, file_size=file_size)
        #)

        self.spin_box.setValue(0)
        self.spin_box.valueChanged.connect(self.__get_hex_data)
        
        # 파일 선택 후 처음 한 번은 hex view를 보여준다.
        self.spin_box.setValue(1)
        self.__get_hex_data()


    def __get_hex_data(self):
        curr_page = self.spin_box.value()
        #if curr_page < self.spin_box.maximum():
        m = self.spin_box.maximum()

        if curr_page < 1 or m < curr_page:
            if curr_page < 1:
                self.spin_box.setValue(1)
            else:
                self.spin_box.setValue(m)
            # QMessageBox.critical(self, 'Alert', f'Select value: {1} ~ {m}')

        if curr_page < m:
            lim = ceil(self.BUFSIZ/0x10)
        else:
            lim = self.file_size % self.BUFSIZ
            lim = ceil((self.BUFSIZ if lim == 0 else lim)/0x10)

        curr_page -= 1
        self.apfs_file.seek(
            self.apfs.msb +
            (self.apfs.block_size*self.block_count) +
            (curr_page*self.BUFSIZ)
        )
        offset = curr_page*self.BUFSIZ
        msg = []
        for _ in range(lim):
            #data: bytes = self.apfs_file.read(0x10)
            data: str = self.apfs_file.read(0x10).hex()
            l = []
            for idx1 in range(0, len(data), 2):
                l.append(data[idx1: (idx1 + 2)])
            output = '%08X:  ' % offset

            for idx2 in range(0x10):
                if idx2 == 8:
                    output += ' '
                output += (l[idx2] + ' ')
            output += '  |'

            for idx3 in range(0x10):
                if 0x20 <= int(l[idx3], 16) <= 0x7E:
                    output += chr(int(l[idx3], 16))
                else:
                    output += '.'
            output += '\n'
            msg.append(output)
            offset += 0x10

        label = QLabel()
        label.setText(''.join(msg))
        label.setFont(QFont('Courier New', 8, QFont.Normal, True))
        label.adjustSize()
        self.hex_area.setWidget(label)


    def __menuBarUI(self):
        menu_bar: QMenuBar = self.main_window.menuBar

        # Create a "Tools" Menu
        tools_menu: QMenu = menu_bar.addMenu('Tools')

        # Create and add a "Metadata" action
        metadata_action = QAction('Metadata', tools_menu)
        metadata_action.triggered.connect(self.__showMetadataUI)
        tools_menu.addAction(metadata_action)

        # Create and add a separator
        tools_menu.addSeparator()

        # Create and add a "Extract" menu
        extract_action = QAction('Extract', tools_menu)
        extract_action.triggered.connect(self.__extract)
        tools_menu.addAction(extract_action)

        menu_bar.show()

    def __metadataUI(self):
        if self.metadata_widget:
            return

        metadata_window = MetadataUI(
            data=self.metadata,
            row_count=len(self.metadata),
            col_count=2 # key, value
        )

        self.metadata_widget = metadata_window.widget
        self.metadata_widget.setHidden(True)

    def __read_metadata(self) -> OrderedDict[str, str]:
        query = \
            f'''
            SELECT key, value
            FROM {DatabaseManager.METADATA_TABLE_NAME}
            '''
        self._cursor.execute(query)
        data = OrderedDict()
        result = self._cursor.fetchall()
        for row in result:
            key, value = row
            data[key] = value

        return data

    def __showMetadataUI(self):
        if not self.metadata_widget:
            self.__metadataUI()

        if self.metadata_widget.isHidden():
            self.metadata_widget.show()

    def __extract(self):
        # Get binary data of file to extract
        selected_row = self.table_widget.currentIndex().row()
        selected_item = self.table_widget.item(selected_row, 0)
        if not selected_item:
            QMessageBox.critical(self, 'Alert', 'Select a file to extract.' )
            return

        selected_name = selected_item.text()
        query = \
            f'''
            SELECT file_size, block_count, group_permission
            FROM `{DatabaseManager.APFS_TABLE_NAME}`
            WHERE name = \'{selected_name}\'
            '''
        try:
            self._cursor.execute(query)
        except sqlite3.OperationalError:
            QMessageBox.critical(self, 'Alert', 'Can\'t read that file.')
            return

        file_size, block_count, group_permission = self._cursor.fetchone()
        file_size = int(file_size)
        block_count = int(block_count)
        group_permission = int(group_permission)

        if group_permission // 0x1000 == 4:
            QMessageBox.critical(self, 'Alert','Cannot extract a directory.')
        else:
            file_to_save, _ = \
                QFileDialog.getSaveFileName(self.table_widget, caption='Save file', directory=f'./{selected_name}', options=QtWidgets.QFileDialog.Options())

            if file_to_save and file_to_save != '':
                try:
                    self.apfs_file.seek(self.apfs.msb + self.apfs.block_size*block_count)
                    bufsiz = (2**10)*(2**10)*16
                    with open(file_to_save, 'wb') as f:
                        for _ in range(file_size // bufsiz):
                            data = self.apfs_file.read(bufsiz)
                            f.write(data)
                            f.flush()  # 메모리 안 먹게 출력 버퍼를 바로바로 비워줌
                        data = self.apfs_file.read(file_size % bufsiz)
                        f.write(data)
                        f.flush()
                except FileNotFoundError:
                    QMessageBox.critical(self, 'Alert', f'No such file or directory: {file_to_save}')
                except:
                    if os.path.exists(file_to_save):
                        os.remove(file_to_save)
