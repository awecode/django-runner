#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtCore import QCoreApplication, QSettings
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QMainWindow, QAction


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
        self.status_bar = self.create_status_bar()
        self.toolbar = self.create_toolbar()
        self.menu_bar = self.create_menu_bar()
        self.setWindowTitle(self.base.settings.value('title'))

    def create_toolbar(self):
        exit_action = QAction(QIcon('exit24.png'), 'Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.quit())
        bar = self.addToolBar('Exit')
        bar.addAction(exit_action)
        return bar

    def create_status_bar(self):
        bar = self.statusBar()
        bar.showMessage(self.base.status_text)
        return bar

    def create_menu_bar(self):
        exit_action = QAction(QIcon('exit.png'), '&Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.quit())
        bar = self.menuBar()
        file_menu = bar.addMenu('&File')
        file_menu.addAction(exit_action)
        return bar

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
