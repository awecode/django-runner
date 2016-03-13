#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtCore import QCoreApplication, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QMainWindow, QAction, qApp


class Tray():
    pass


class DRBase(object):
    def __init__(self, *args, **kwargs):
        self.settings = QSettings("settings.ini", QSettings.IniFormat)
        self.status_text = 'Loading ...'
        self.cockpit = Cockpit(self)


class Cockpit(QMainWindow):
    def __init__(self, base):
        super(Cockpit, self).__init__()
        self.base = base
        self.createStatusBar()
        self.createMenuBar()
        self.setWindowTitle(self.base.settings.value('title'))

    def createStatusBar(self):
        self.statusbar = self.statusBar()
        self.statusbar.showMessage(self.base.status_text)

    def createMenuBar(self):
        exitAction = QAction(QIcon('exit.png'), '&Exit', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Exit application')
        exitAction.triggered.connect(self.quit())
        self.menubar = self.menuBar()
        fileMenu = self.menubar.addMenu('&File')
        fileMenu.addAction(exitAction)

    def show_window(self):
        self.center()
        self.show()

    def quit(self):
        return QCoreApplication.instance().quit

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def closeEvent(self, event):
        # noinspection PyCallByClass
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    base = DRBase()
    base.cockpit.show_window()
    sys.exit(app.exec_())
