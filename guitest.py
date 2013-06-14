import sys, os
import PySide.QtCore

#This magic gets the Guru directory.
lib_path = os.path.dirname(sys.argv[0])
lib_path = os.path.abspath(lib_path)
lib_path = os.path.join(lib_path, "lib")
sys.path.append(lib_path)

#from PySide import QtCore, QtGui
from PySide.QtGui import QApplication
from guru.MainWindow import MainWindow

app = QApplication(sys.argv)
main_window = MainWindow(isWelcome=True)
main_window.show()
main_window.activateWindow() #This does not work for some reason.
app.exec_()