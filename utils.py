from PyQt5.QtCore import pyqtRemoveInputHook
import os
import sys
import subprocess
import shutil
from psutil import process_iter
from psutil import AccessDenied
from signal import SIGTERM  # or SIGKILL
from ipdb import set_trace
from glob import glob
from sys import executable



def debug_trace():
    pyqtRemoveInputHook()
    set_trace()


def which(program):
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


def move_files(src, dst):
    for src_dir, dirs, files in os.walk(src):
        dst_dir = src_dir.replace(src, dst, 1)
        if not os.path.exists(dst_dir):
            os.makedirs(dst_dir)
        for file_ in files:
            src_file = os.path.join(src_dir, file_)
            dst_file = os.path.join(dst_dir, file_)
            if os.path.exists(dst_file):
                os.remove(dst_file)
            shutil.move(src_file, dst_dir)


def call_command(param, cwd=None):
    if sys.platform == "win32":
        param.insert(0, 'cmd.exe')
        param.insert(1, '/K')
        subprocess.Popen(param, cwd=cwd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        original_command = ' '.join(param)
        # param.insert(0, 'gnome-terminal')
        # param.insert(1, '-e')
        # print(param)
        cmd = ['gnome-terminal', '-x', 'bash', '-c', '"'+original_command+'; bash"']
        print(' '.join(cmd))
        print(cwd)
        subprocess.Popen(cmd, cwd=cwd, shell=True)


def clean_pyc(folder):
    folder = folder.rstrip('/').rstrip('\\')
    for file in glob(os.path.join(folder, '**', '*.pyc'), recursive=True):
        os.remove(file)


def free_port(port):
    for proc in process_iter():
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr[1] == int(port):
                    proc.send_signal(SIGTERM)  # or SIGKILL
                    continue
        except AccessDenied:
            continue


def process_on_port(port):
    for proc in process_iter():
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr[1] == int(port):
                    return proc
                    continue
        except AccessDenied:
            continue


def confirm_process_on_port(port, cmdline):
    for proc in process_iter():
        try:
            for conns in proc.connections(kind='inet'):
                if conns.laddr[1] == int(port):
                    if proc.cmdline() == cmdline:
                        return True
                    continue
        except AccessDenied:
            continue
    return False
