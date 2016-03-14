#!/usr/bin/python3
# -*- coding: utf-8 -*-


import sys
from PyQt5.QtCore import QCoreApplication, QSettings, Qt, QObject, pyqtSignal, QSize, QUrl, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMessageBox, QDesktopWidget, QMainWindow, QAction, QHBoxLayout, \
    QVBoxLayout, QLCDNumber, QSlider, QFileDialog, QSystemTrayIcon, QMenu, QTabWidget, QTabBar, QFormLayout, QLineEdit, \
    QRadioButton, QLabel


class Tray(QSystemTrayIcon):
    def __init__(self, base):
        super(Tray, self).__init__(base.app_icon, app)
        self.base = base
        self.cockpit = base.cockpit
        self.menu = self.create_menu()
        self.setToolTip(base.settings.value('title'))

    def create_menu(self):
        menu = QMenu(self.cockpit)
        title = menu.addAction(QIcon('icons/awecode/16.png'), self.base.settings.value('title'))
        title.triggered.connect(self.base.web_view.start)
        menu.addSeparator()
        view_shell = menu.addAction(QIcon.fromTheme('text-x-script'), '&View Shell')
        view_shell.triggered.connect(self.base.quit)
        settings = menu.addAction(QIcon.fromTheme('emblem-system'), 'Set&tings')
        settings.triggered.connect(self.base.quit)
        about = menu.addAction(QIcon.fromTheme('help-about'), '&About')
        about.triggered.connect(self.base.quit)
        backup_restore = menu.addAction(QIcon.fromTheme('media-seek-backward'), '&Backup/Restore')
        backup_restore.triggered.connect(self.base.quit)
        check_update = menu.addAction(QIcon.fromTheme('system-software-update'), 'Check for &Updates')
        check_update.triggered.connect(self.base.quit)
        menu.addSeparator()
        exit_action = menu.addAction(QIcon.fromTheme('exit'), 'E&xit')
        exit_action.triggered.connect(self.cockpit.quit)

        self.setContextMenu(menu)
        self.show()


class Tab(QWidget):
    def __init__(self, *args, **kwargs):
        self.tab_widget = kwargs.pop('tab_widget')
        super(Tab, self).__init__(*args, **kwargs)
        self.tab_widget.addTab(self, self.__class__.__name__)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.add_content()

    def add_content(self):
        pass


class Service(Tab):
    def add_content(self, *args, **kwargs):
        pushButton1 = QPushButton("Start")
        self.layout.addWidget(pushButton1)


class Settings(Tab):
    pass


class WebView(QWebView):
    def __init__(self, base):
        super(WebView, self).__init__()
        self.base = base

    def start(self):
        self.load(QUrl('http://127.0.0.1:8000'))
        self.show()


class Communicate(QObject):
    close_app = pyqtSignal()


class DRBase(object):
    def __init__(self, *args, **kwargs):
        self.app_icon = self.set_icon()
        self.settings = QSettings("settings.ini", QSettings.IniFormat)
        self.status_text = 'Loading ...'
        self.cockpit = Cockpit(self)
        self.web_view = WebView(self)
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
        self.widget = self.create_widget()
        self.status_bar = self.create_status_bar()
        self.create_tabs()
        self.show_window()

    def create_widget(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)
        return widget

    def create_tabs(self):
        tab_widget = QTabWidget(self.widget)
        # tab_widget.setGeometry(QRect(10, 10, 500, 500))
        self.service_tab = Service(tab_widget=tab_widget)
        self.setting_tab = Settings(tab_widget=tab_widget)
        return tab_widget

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
        reply = QMessageBox.question(self, 'Exit', "Are you sure you want to stop the service?", QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
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


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons/awecode/16.png'))
    base = DRBase()

    # tab = Tab(base.cockpit)
    base.cockpit.show_window()
    # tab.show()
    sys.exit(app.exec_())
