import sys

import PyQt5, sqlite3

from PyQt5 import QtWidgets
from gui.start import StartUI

def main():
    app = QtWidgets.QApplication(sys.argv)
    StartUI()
    app.exec_()

if __name__ == '__main__':
    main()


