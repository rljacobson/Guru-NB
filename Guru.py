import sys

from guru.globals import startServerThread, cleanup



from PySide.QtGui import QApplication
from guru.MainWindow import MainWindow

def main():
    #Start the Flask server in a new thread.
    startServerThread()

    #Now start the main UI.
    app = QApplication(sys.argv)
    app.setOrganizationName("Guru")
    app.setOrganizationDomain("rwu.edu")
    app.setApplicationName("Guru")

    main_window = MainWindow(isWelcome=True)
    main_window.show()
    main_window.activateWindow() #This does not work for some reason.
    main_window.raise_()         #But this does.
    app.exec_()

    cleanup()

main()