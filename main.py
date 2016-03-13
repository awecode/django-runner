#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtCore import QCoreApplication, QSettings, Qt, QObject, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QMainWindow, QAction, QHBoxLayout, \
    QVBoxLayout, QLCDNumber, QSlider, QFileDialog


class Tray():
    pass


class Communicate(QObject):
    close_app = pyqtSignal()


class DRBase(object):
    def __init__(self, *args, **kwargs):
        self.settings = QSettings("settings.ini", QSettings.IniFormat)
        self.status_text = 'Loading ...'
        self.cockpit = Cockpit(self)


class Cockpit(QMainWindow):
    def __init__(self, base):
        super(Cockpit, self).__init__()
        self.base = base
        self.init_UI()

    def init_UI(self):
        self.status_bar = self.create_status_bar()
        self.toolbar = self.create_toolbar()
        self.menu_bar = self.create_menu_bar()
        self.setWindowTitle(self.base.settings.value('title'))
        self.resize(300, 300)
        self.show()

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
        exit_action = QAction(QIcon('exit.png'), 'E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.quit())

        restore_action = QAction(QIcon('exit.png'), '&Restore', self)
        restore_action.setShortcut('Ctrl+R')
        restore_action.setStatusTip('Restore Database')
        restore_action.triggered.connect(self.show_file_dialog)

        bar = self.menuBar()
        file_menu = bar.addMenu('&File')
        file_menu.addAction(exit_action)
        file_menu.addAction(restore_action)
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

    def show_file_dialog(self):
        file_name = QFileDialog.getOpenFileName(self, 'Open database file to restore', '')

    # def mousePressEvent(self, event):
    #     self.c.closeApp.emit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

            # def closeEvent(self, event):
            #     # noinspection PyCallByClass
            #     reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            #     if reply == QMessageBox.Yes:
            #         event.accept()
            #     else:
            #         event.ignore()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    base = DRBase()
    base.cockpit.show_window()
    sys.exit(app.exec_())
