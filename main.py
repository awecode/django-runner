#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtCore import QCoreApplication, QSettings, Qt, QObject, pyqtSignal, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QMainWindow, QAction, QHBoxLayout, \
    QVBoxLayout, QLCDNumber, QSlider, QFileDialog, QSystemTrayIcon, QMenu


class Tray(QSystemTrayIcon):
    def __init__(self, base):
        super(Tray, self).__init__(base.app_icon, app)
        self.base = base
        self.menu = self.create_menu()

    def create_menu(self):
        menu = QMenu(self.base.cockpit)
        exit_action = menu.addAction("E&xit")
        exit_action.triggered.connect(self.base.quit)
        self.setContextMenu(menu)
        self.show()


class Communicate(QObject):
    close_app = pyqtSignal()


class DRBase(object):
    def __init__(self, *args, **kwargs):
        self.app_icon = self.set_icon()
        self.settings = QSettings("settings.ini", QSettings.IniFormat)
        self.status_text = 'Loading ...'
        self.cockpit = Cockpit(self)
        self.tray = Tray(self)

    def quit(self):
        return QCoreApplication.instance().quit()

    def set_icon(self):
        app_icon = QIcon()
        app_icon.addFile('icons/awecode/16.png', QSize(16, 16))
        app_icon.addFile('icons/awecode/24.png', QSize(24, 24))
        app_icon.addFile('icons/awecode/32.png', QSize(32, 32))
        app_icon.addFile('icons/awecode/48.png', QSize(48, 48))
        app_icon.addFile('icons/awecode/256.png', QSize(256, 256))
        app.setWindowIcon(QIcon('icons/awecode/16x16.png'))
        return app_icon


class Cockpit(QMainWindow):
    def __init__(self, base):
        super(Cockpit, self).__init__()
        self.base = base
        self.init_UI()

    def init_UI(self):
        self.status_bar = self.create_status_bar()
        # self.toolbar = self.create_toolbar()
        self.menu_bar = self.create_menu_bar()
        self.show_window()

    def create_toolbar(self):
        exit_action = QAction(QIcon.fromTheme('exit'), 'Exit', self)
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
        exit_action = QAction(QIcon.fromTheme('exit'), 'E&xit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.setStatusTip('Exit application')
        exit_action.triggered.connect(self.quit)

        restore_action = QAction(QIcon.fromTheme('system-software-update'), '&Restore', self)
        restore_action.setShortcut('Ctrl+R')
        restore_action.setStatusTip('Restore Database')
        restore_action.triggered.connect(self.show_file_dialog)

        bar = self.menuBar()
        file_menu = bar.addMenu('&File')
        file_menu.addAction(exit_action)
        file_menu.addAction(restore_action)
        return bar

    def show_window(self):
        self.setWindowTitle(self.base.settings.value('title'))
        self.setWindowIcon(self.base.app_icon)
        self.resize(300, 300)
        self.center()
        self.show()

    def quit(self):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            return self.base.quit()

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
    app.setWindowIcon(QIcon('icons/awecode/16.png'))
    base = DRBase()
    base.cockpit.show_window()
    sys.exit(app.exec_())
