#!/usr/bin/python3

import sys
import os


from supsisim.qtvers import *

from supsisim.library import Library

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filename = sys.argv[1]
        if filename[-4:] != '.dgm':
            filename = filename + '.dgm'
        if not os.path.isfile(filename):
            filename = 'untitled'
    else:
        filename = 'untitled'

    if filename!='untitled':
        fname = QFileInfo(filename)
        mypath = str(fname.absolutePath())
        fname = str(fname.baseName())
    else:
        fname = 'untitled'
        mypath =  os.getcwd()

    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    rect = screen.availableGeometry()
    h = int(rect.height()*0.9)
    
    library = Library()
    library.setGeometry(0, 0, 400, h)
    library.setMaximumSize(400,h)
    library.setMinimumSize(400,h)
    library.show()
    library.setWindowState(Qt.WindowState.WindowMaximized)
       
    if fname == 'untitled':
        library.newFile()
        library.setWindowState(Qt.WindowState.WindowMaximized)
    else:
        library.fopen(fname)
        library.setWindowState(Qt.WindowState.WindowMinimized)
    ret = app.exec()
    app.deleteLater()

