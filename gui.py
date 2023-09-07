import sqlite3

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import *

class MyApp(QWidget):
    global conn
    global c
    global table
    global table_lst
    global QTree
    global QTable
    global QTab
    global tab1
    global tab2
    global label
    global scrollArea
    global font
    global apfs
    global f
    global blockCount

    def __init__(self, apfs_tmp, f):
        super().__init__()
        self.conn=sqlite3.connect("apfs.db", isolation_level=None)
        self.c=self.conn.cursor()
        self.table_lst=[]
        self.c.execute("select name from sqlite_master where type='table';")
        for i in self.c.fetchall():
            self.table_lst.append(i[0])
        self.apfs=apfs_tmp
        self.f=f
        self.initUI()

    def initUI(self):
        self.fname=str(self.f).replace("/", "\\").split('\\')[-1][:-2]
        self.treeUI()

        self.QTable = QTableWidget(0, 4)
        self.QTable.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.QTable.setHorizontalHeaderLabels(["Name", "Size", "Type", "Date Modified"])
        self.QTable.setAutoScroll(True)
        self.QTable.verticalHeader().setVisible(False)
        self.QTable.setColumnWidth(0, 250)
        self.QTable.setColumnWidth(1, 100)
        self.QTable.setColumnWidth(2, 100)
        self.QTable.setColumnWidth(3, 200)

        self.tab1=QWidget()
        self.tab2=QWidget()
        self.QTab=QTabWidget()
        self.QTab.addTab(self.tab1, 'Hex')
        self.label=QLabel()
        self.font=QFont("DejaVu Sans Mono", 8, QFont.Normal, True)
        self.scrollArea=QScrollArea()

        self.QTree.itemClicked.connect(self.tableUI)
        self.QTable.itemClicked.connect(self.hexUI)

        window = QGridLayout()
        window.addWidget(self.QTree, 0, 0, 3, 1)
        window.addWidget(self.QTable, 0, 1, 1, 1)
        window.addWidget(self.scrollArea, 2, 1, 1, 1)
        self.setLayout(window)
        self.setGeometry(300, 300, 1000, 700)
        self.setWindowTitle('APFS - '+self.fname)
        self.show()


    def treeUI(self):
        self.QTree = QTreeWidget()
        self.QTree.setMaximumWidth(300)

        parent = QTreeWidgetItem(self.QTree)
        parent.setText(0, self.apfs.file_name)
        for i in self.table_lst:
            child=QTreeWidgetItem(parent)
            child.setText(0, i)
            self.findParent(i, child, '0x1')

    def findParent(self, table_name, parent, parent_id):
        query = f'SELECT * from {table_name} \
                  WHERE ParentFolderID=\'{parent_id}\' \
                    AND GroupPermission/4096=4'
        self.c.execute(query)
        result = self.c.fetchall()
        for i in range(len(result)):
            child = QTreeWidgetItem(parent)
            child.setText(0, result[i][12])             #12번 인덱스가 파일 이름
            self.findParent(table_name, child, result[i][1])        #1번 인덱스가 parent id

    def tableUI(self):
        selectedFile = self.QTree.currentItem()
        if selectedFile.text(0) == self.apfs.file_name:
            return
        tmp = selectedFile
        while True:
            if tmp.parent().text(0) == self.apfs.file_name:
                break
            tmp = tmp.parent()
        self.table = tmp.text(0)
        self.c.execute(f"SELECT FileID FROM {tmp.text(0)} WHERE Name='{selectedFile.text(0)}'")
        parent_id=self.c.fetchone()[0]
        query = f"SELECT Name, FileSize, GroupPermission, LastWrittenDate \
                    FROM {tmp.text(0)} \
                    WHERE ParentFolderID = '{parent_id}' \
                    AND blockCount NOT NULL"
        self.c.execute(query)
        result=self.c.fetchall()
        count=len(result)
        self.QTable.setRowCount(count)
        for i in range(count):
            Name, FileSize, GroupPermission, LastWrittenDate = result[i]
            self.QTable.setItem(i, 0, QTableWidgetItem(Name))
            self.QTable.setItem(i, 1, QTableWidgetItem(FileSize))
            if int(GroupPermission) // 0x1000 == 8:
                self.QTable.setItem(i, 2, QTableWidgetItem("File"))
            else:
                self.QTable.setItem(i, 2, QTableWidgetItem("Folder"))
            self.QTable.setItem(i, 3, QTableWidgetItem(LastWrittenDate))

    def hexUI(self):
        row=self.QTable.currentIndex().row()
        selectedFileName = self.QTable.item(row, 0).text()

        self.c.execute("select FileSize, BlockCount, GroupPermission from " + self.table + " \
                        where Name='" + selectedFileName + "'")
        fileSize, blockCount, groupPermission=self.c.fetchone()
        if int(groupPermission)//0x1000 == 4:
            msg = "This is folder."
        else:
            if not blockCount:
                print('Can\'t read this file.')
                QMessageBox.about(self, '알림', '파일을 찾을 수 없습니다.')
                return
            self.f.seek(self.apfs.MSB+self.apfs.block_size*int(blockCount))
            msg = []
            offset = 0
            for i in range(int(fileSize) // 0x10):
                data = self.f.read(0x10).hex()
                lst = []
                [lst.append(data[i : (i + 2)]) for i in range(0, len(data), 2)]
                output = '%08X:  ' % (offset)
                for i in range(0x10):
                    if(i == 8):
                        output += ' '
                    output += lst[i] + ' '
                output += '  |'

                for i in range(0x10):
                    if(int(lst[i], 16) >= 0x20 and int(lst[i], 16) <= 0x7E):
                        output += chr(int(lst[i], 16))
                    else:
                        output += '.'
                output += '\n'
                msg.append(output)
                offset += 0x10
            msg = ''.join(msg)
        self.label.setText(msg)
        self.label.setFont(self.font)
        self.label.adjustSize()
        self.scrollArea.setWidget(self.label)

    def contextMenuEvent(self, event):
        menu=QMenu(self)
        extract_action=menu.addAction("Extract")
        action=menu.exec_(self.mapToGlobal(event.pos()))
        if action == extract_action:
            row = self.QTable.currentIndex().row()
            selectedFileName = self.QTable.item(row, 0).text()
            self.c.execute("select FileSize, BlockCount, GroupPermission from " + self.table + " \
                                    where Name='" + selectedFileName + "'")
            fileSize, blockCount, groupPermission = self.c.fetchone()
            if int(groupPermission) // 0x1000 == 4:
                print("This is folder.")
            else:
                saveFile = QFileDialog.getSaveFileName(self, 'Save file', './')

                '''
                f=open(saveFile[0], "wb")
                self.f.seek(self.apfs.MSB + self.apfs.block_size * int(blockCount))
                data=self.f.read(int(fileSize))
                f.write(data)
                '''
                try:
                    with open(saveFile[0], 'wb') as file:
                        self.f.seek(self.apfs.MSB + self.apfs.block_size * int(blockCount))
                        
                        size = int(fileSize)
                        bufsiz = 2048
                        data = self.f.read(bufsiz)
                        while data:
                            file.write(data)
                            file.flush()
                            data = self.f.read(bufsiz)
                except:
                    print(f'No such file or firectory: {saveFile[0]}')
