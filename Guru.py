import sys

#Start the Flask server in a new thread.
from guru.globals import startServerThread, cleanup
startServerThread()

#Now start the main UI.
from PySide.QtGui import QApplication
from guru.MainWindow import MainWindow

app = QApplication(sys.argv)
main_window = MainWindow(isWelcome=True)
main_window.show()
main_window.activateWindow() #This does not work for some reason.
main_window.raise_()         #But this does.
app.exec_()

cleanup()