#!/usr/bin/python3
# -*- coding: utf-8 -*-
import os
import signal
import subprocess
import sys

from PyQt5.QtCore import QCoreApplication, QSettings, Qt, pyqtSignal, QSize, QUrl, QThread, QProcess, QObject, pyqtSlot
from PyQt5.QtGui import QIcon, QTextCursor, QPixmap
from PyQt5.QtWebKitWidgets import QWebView
from PyQt5.QtWidgets import QApplication, QWidget, QMessageBox, QDesktopWidget, QMainWindow, QAction, QVBoxLayout, \
    QFileDialog, QSystemTrayIcon, QMenu, QTabWidget, QLabel, QTextEdit, QHBoxLayout, QPushButton, QFormLayout, QLineEdit


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
        view_shell.triggered.connect(lambda: self.show_tab(1))
        settings = menu.addAction(QIcon.fromTheme('emblem-system'), 'Set&tings')
        settings.triggered.connect(self.open_settings_file)
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

    def open_settings_file(self):
        open_file('settings.ini')

    def show_tab(self, tab_index):
        self.base.cockpit.tabs.setCurrentIndex(tab_index)
        self.base.cockpit.show()
        self.base.cockpit.activateWindow()


class Settings(QSettings):
    def __init__(self):
        super(Settings, self).__init__("settings.ini", QSettings.IniFormat)

    def get_python_path(self):
        if self.value('python_path') or self.value('virtualenv_path'):
            return str(self.value('python_path')) or str(os.path.join(self.value('virtualenv_path'), 'bin', 'python'))
        else:
            python_path = which('python')
            if python_path:
                return python_path
            else:
                raise NotImplementedError('Set python or virtualenv path in settings')

    def get_host(self):
        if self.value('host'):
            return self.value('host')
        return '0.0.0.0'

    def get_about_text(self):
        if self.value('about_text'):
            return self.value('about_text')
        return 'Product of <strong>Awecode</strong>'

    def get_port(self):
        if self.value('port'):
            return int(self.value('port'))
        return 8888

    def get_db_file(self):
        if self.value('db_file'):
            return self.value('db_file')
        return 'db.sqlite3'

    def get_db_file_path(self):
        return os.path.join(self.value('project_path'), self.get_db_file())

    def get_addr(self):
        return self.get_host() + ':' + str(self.get_port())

    def get_url(self):
        return 'http://' + self.get_addr()

    def get_backup_dir(self):
        self.beginGroup('History')
        backup_dir = self.value('backup_dir')
        self.endGroup()
        return backup_dir

    def get_backup_file_path(self):
        self.beginGroup('History')
        backup_file_val = self.value('backup_file')
        self.endGroup()
        if backup_file_val and os.path.isfile(backup_file_val):
            backup_file = backup_file_val
        elif os.path.isfile(self.get_db_file_path()):
            backup_file = self.get_db_file_path()
        else:
            backup_file = None
        return backup_file


class Tab(QWidget):
    def __init__(self, *args, **kwargs):
        self.tab_widget = kwargs.pop('tab_widget')
        self.settings = self.tab_widget.settings
        super(Tab, self).__init__(*args, **kwargs)
        self.tab_widget.addTab(self, self.__class__.__name__.replace('Tab', ''))
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.add_content()

    def add_content(self):
        pass

    def add(self, content):
        self.layout.addWidget(content)

    def add_line(self, content):
        label = QLabel(str(content))
        self.add(label)


class ServiceThread(QThread):
    line_output = pyqtSignal(str)
    line_error = pyqtSignal(str)

    def __init__(self):
        QThread.__init__(self)

    def __del__(self):
        self.wait()

    def run(self):
        from subprocess import Popen, PIPE

        print('a')
        env = os.environ.copy()
        env["PATH"] = "/home/xtranophilist/pro/goms/env/bin:" + env["PATH"]
        try:
            self.proc = Popen(['python', 'manage.py', 'runserver'], cwd='/home/xtranophilist/pro/goms/app',
                              stdin=PIPE, stdout=PIPE, stderr=PIPE, shell=False, env=env)
            while True:
                output = self.proc.stdout.readline().decode('utf-8')
                if output:
                    self.line_output.emit(output)
                else:
                    break
            while True:
                error = self.proc.stderr.readline().decode('utf-8')
                if error:
                    self.line_error.emit(error)
                else:
                    break
        except FileNotFoundError as e:
            self.line_error.emit(str(e))
            self.proc = None
            self.terminate()


class Log(QTextEdit):
    def __init__(self):
        super(Log, self).__init__()
        self.setReadOnly(True)
        self.setLineWrapMode(QTextEdit.NoWrap)
        self.setStyleSheet("color: white; background: black")
        font = self.font()
        font.setFamily("Courier")
        font.setPointSize(10)
        self.html = ''

    def add_line(self, st):
        self.moveCursor(QTextCursor.End)
        self.html += '<pre>' + st + '</pre>'
        self.setHtml(self.html)
        sb = self.verticalScrollBar()
        sb.setValue(sb.maximum())
        self.updateGeometry()

    def add_warning(self, st):
        self.add_line('<span style="color:yellow">' + st + '</span>')

    def add_error(self, st):
        self.add_line('<span style="color:red">' + st + '</span>')


class Worker(QObject):
    response = pyqtSignal(str)

    def __init__(self, settings):
        super().__init__()
        self.settings = settings

    def work(self):
        import socket

        while True:
            import time

            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((self.settings.get_host(), self.settings.get_port()))
            if result == 0:
                self.response.emit('Started')
            else:
                self.response.emit('Stopped')
            time.sleep(2)


class ServiceTab(Tab):
    def set_process_status(self, st):
        self.process_status = st
        self.status_text.setText(st)
        if self.process_status == 'Started':
            self.start_button.setEnabled(False)
        else:
            self.start_button.setEnabled(True)
        if self.process_status == 'Stopped':
            self.stop_button.setEnabled(False)
        else:
            self.stop_button.setEnabled(True)

    # def restart_process(self):
    #     self.stop_process()
    #     self.start_process()

    def start_process(self):
        self.set_process_status('Stopped')
        self.process.kill()
        if self.settings.value('project_path'):
            self.process.setWorkingDirectory(self.settings.value('project_path'))
        process_args = ['manage.py', 'runserver', '--noreload']
        process_args.append(self.settings.get_addr())
        self.process.start(self.settings.get_python_path(), process_args)
        app.aboutToQuit.connect(self.stop_process)
        self.thread = QThread(app)
        self.w = Worker(self.settings)
        self.w.response[str].connect(self.port_response)
        self.w.moveToThread(self.thread)
        self.thread.started.connect(self.w.work)
        self.thread.start()

    @pyqtSlot(str)
    def port_response(self, str):
        self.set_process_status(str)

    def stop_process(self):
        self.process.kill()
        self.console.add_warning('Stopped process.')
        self.set_process_status('Stopped')

    def add_content(self, *args, **kwargs):
        self.console = Log()
        self.layout.addWidget(self.console)
        self.footer_layout = QHBoxLayout()
        self.footer_layout.addStretch(1)
        self.layout.addLayout(self.footer_layout)
        status_label = QLabel('Status: ')
        self.status_text = QLabel()
        self.footer_layout.addWidget(status_label)
        self.footer_layout.addWidget(self.status_text)
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_process)
        self.stop_button = QPushButton('Stop')
        self.stop_button.clicked.connect(self.stop_process)
        self.footer_layout.addWidget(self.start_button)
        self.footer_layout.addWidget(self.stop_button)
        # self.restart_button = QPushButton('Restart')
        # self.restart_button.clicked.connect(self.restart_process)
        # self.footer_layout.addWidget(self.restart_button)
        self.process = QProcess(app)
        self.process.readyRead.connect(self.on_ready)
        self.process.error.connect(self.on_error)
        self.process.finished.connect(self.on_finish)
        self.start_process()

    def on_ready(self):
        txt = str(self.process.readAll(), encoding='utf-8')
        self.console.add_line(txt)

    def on_finish(self):
        if not self.process_status[0:4] == 'Stop':
            error = str(self.process.readAllStandardError(), encoding='utf-8')
            if error == '':
                self.console.add_line('Process finished!')
            else:
                self.console.add_error(error)
        self.set_process_status('Stopped')

    def on_error(self):
        if not self.process_status[0:4] == 'Stop':
            error = 'Error occurred while trying to run service.'
            if not self.process.error() == 0:
                error += str(self.process.error())
            self.console.add_error(error)
        self.set_process_status('Stopped')


class SettingsTab(Tab):
    def add_content(self):
        form = QFormLayout(self)
        self.layout.addLayout(form)
        python_path_label = QLabel('Python Executable Path', self)
        python_path_edit = QLineEdit(self)
        form.addRow(python_path_label, python_path_edit)

        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch(1)
        self.layout.addLayout(buttons_layout)
        save_button = QPushButton('Save', self)
        save_button.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_button)

    def save_settings(self):
        print('save')
        pass


class BackupTab(Tab):
    def add_content(self):
        backup_file_row = QHBoxLayout()
        self.layout.addLayout(backup_file_row)
        backup_file_row.addWidget(QLabel('File to be backed up:'))

        self.backup_file = self.settings.get_backup_file_path()
        self.backup_file_label = QLabel(self.backup_file)
        backup_file_row.addWidget(self.backup_file_label)
        self.choose_backup_file_btn = QPushButton('Choose File')
        self.choose_backup_file_btn.clicked.connect(self.choose_backup_file)
        backup_file_row.addWidget(self.choose_backup_file_btn)

        backup_dir_row = QHBoxLayout()
        self.layout.addLayout(backup_dir_row)
        backup_dir_row.addWidget(QLabel('Folder to be backed up to:'))

        self.backup_dir = self.settings.get_backup_dir()
        self.backup_dir_label = QLabel(self.backup_dir)
        backup_dir_row.addWidget(self.backup_dir_label)
        self.choose_backup_dir_btn = QPushButton('Choose Folder')
        self.choose_backup_dir_btn.clicked.connect(self.choose_backup_dir)
        backup_dir_row.addWidget(self.choose_backup_dir_btn)

        self.backup_button = QPushButton('Back up')
        # self.backup_button.clicked.connect(self.choose_backup_dir)
        self.layout.addWidget(self.backup_button)
        self.check_backup_possible()
        
    def check_backup_possible(self):
        if self.backup_dir and os.path.isfile(self.backup_file) and os.path.exists(self.backup_dir) and os.path.isdir(self.backup_dir):
            self.backup_button.setEnabled(True)
            return True
        else:
            self.backup_button.setEnabled(False)
            return False

    def choose_backup_file(self):
        chosen = QFileDialog.getOpenFileName(self, 'Choose database file to backup', '')
        if os.path.isfile(chosen[0]):
            self.backup_file = chosen[0]
        elif not chosen[0]:
            return
        else:
            self.choose_backup_file()
        self.settings.beginGroup('History')
        self.settings.setValue('backup_file', self.backup_file)
        self.settings.endGroup()
        self.backup_file_label.setText(self.backup_file)
        self.check_backup_possible()

    def choose_backup_dir(self):
        self.backup_dir = str(QFileDialog.getExistingDirectory(self, "Select directory to backup the database file to..."))
        if os.path.exists(self.backup_dir) and os.path.isdir(self.backup_dir):
            self.settings.beginGroup('History')
            self.settings.setValue('backup_dir', self.backup_dir)
            self.settings.endGroup()
            self.backup_dir_label.setText(self.backup_dir)
        self.check_backup_possible()


class AboutTab(Tab):
    def add_content(self):
        # self.inner_layout = QHBoxLayout()
        # self.layout.addLayout(self.inner_layout)
        self.layout.setAlignment(Qt.AlignHCenter)
        pic = QLabel(self)
        pic.setGeometry(10, 10, 400, 100)
        pic.setPixmap(QPixmap(os.path.join(os.getcwd(), 'icons', 'awecode', '256.png')))
        self.layout.addWidget(pic)
        about_text = self.settings.get_about_text()
        text = QLabel(about_text, self)
        self.layout.addWidget(text)


class WebView(QWebView):
    def __init__(self, base):
        super(WebView, self).__init__()
        self.base = base

    def start(self):
        self.load(QUrl(self.base.settings.get_url()))
        self.show()


class DRBase(object):
    def __init__(self, *args, **kwargs):
        self.app_icon = self.set_icon()
        self.settings = Settings()
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
        self.tabs = self.create_tabs()
        self.show_window()

    def create_widget(self):
        widget = QWidget(self)
        self.setCentralWidget(widget)
        layout = QVBoxLayout()
        widget.setLayout(layout)
        return widget

    def create_tabs(self):
        tab_widget = QTabWidget()
        tab_widget.settings = self.base.settings
        self.service_tab = ServiceTab(tab_widget=tab_widget)
        # self.setting_tab = SettingsTab(tab_widget=tab_widget)
        self.backup_tab = BackupTab(tab_widget=tab_widget)
        self.about_tab = AboutTab(tab_widget=tab_widget)
        self.widget.layout().addWidget(tab_widget)
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
        self.resize(1000, 15000)
        # self.showMaximized()
        self.center()
        self.show()

    def quit(self):
        reply = QMessageBox.question(self, 'Exit', "Are you sure you want to exit and stop the service?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.No)
        if reply == QMessageBox.Yes:
            return self.base.quit()

    def center(self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    # def mousePressEvent(self, event):
    #     self.c.closeApp.emit()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def closeEvent(self, event):
        event.ignore()
        self.hide()


def debug_trace():
    from PyQt5.QtCore import pyqtRemoveInputHook

    from pdb import set_trace

    pyqtRemoveInputHook()
    set_trace()


def which(program):
    import os

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None


def open_file(filename):
    if sys.platform == "win32":
        os.startfile(filename)
    else:
        opener = "open" if sys.platform == "darwin" else "xdg-open"
        subprocess.call([opener, filename])


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setWindowIcon(QIcon('icons/awecode/16.png'))
    base = DRBase()
    base.cockpit.show_window()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    ret = app.exec_()
    app.deleteLater()
    sys.exit(ret)
