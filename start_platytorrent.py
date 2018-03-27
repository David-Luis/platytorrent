from PyQt5 import QtGui, QtCore, QtNetwork, QtWidgets
from PyQt5.QtWidgets import QApplication

from src.model.TorrentModel import TorrentModel
from src.view.MainView import MainView
from src.controller.TorrentController import TorrentController

from src.model import ThreadsManager

import psutil
import os
import platform
import time

def kill_proc_tree(pid, including_parent=True):
    parent = psutil.Process(pid)
    for child in parent.children(recursive=True):
        child.kill()
    if including_parent:
        parent.kill()

def process_args(model):
    if len(sys.argv) > 1:
        controller.add_magnet_or_torrent(sys.argv[1])

class SingleApplication(QtWidgets.QApplication):
    messageAvailable = QtCore.pyqtSignal(object)

    def __init__(self, argv, key):
        QtWidgets.QApplication.__init__(self, argv)
        self._memory = QtCore.QSharedMemory(self)
        self._memory.setKey(key)
        if self._memory.attach():
            self._running = True
        else:
            self._running = False
            if not self._memory.create(1):
                raise RuntimeError(self._memory.errorString())

    def isRunning(self):
        return self._running

class SingleApplicationWithMessaging(SingleApplication):
    def __init__(self, argv, key):
        SingleApplication.__init__(self, argv, key)

        self._key = key
        self._timeout = 1000
        self._server = QtNetwork.QLocalServer(self)
        if not self.isRunning():
            #print("LISTENING IN " + self._key)
            self._server.newConnection.connect(self.handleMessage)
            self._server.listen(self._key)

    def handleMessage(self):
        socket = self._server.nextPendingConnection()
        if socket.waitForReadyRead(self._timeout):
            self.messageAvailable.emit(
                socket.readAll().data().decode('utf-8'))
            socket.disconnectFromServer()
        else:
            QtCore.qDebug(socket.errorString())

    def sendMessage(self, message):
        if self.isRunning():
            socket = QtNetwork.QLocalSocket(self)
            socket.connectToServer(self._key, QtCore.QIODevice.WriteOnly)
            if not socket.waitForConnected(self._timeout):
                print("ERROR sendMessage 1: " + socket.errorString())
                return False
            if not isinstance(message, bytes):
                message = message.encode('utf-8')
            socket.write(message)
            if not socket.waitForBytesWritten(self._timeout):
                print("ERROR sendMessage 2: " + socket.errorString())
                return False
            socket.disconnectFromServer()
            return True
        return False

def focus_window():
    view.focusWindow()

def handleMessage(message):
    print(message)
    if message == "focusWindow":
        focus_window()
    else:
        controller.add_magnet_or_torrent(message)
        focus_window()

if __name__ == '__main__':

    import sys

    key = 'Platytorrent'

    system = platform.system().lower()
    if "windows" in system:
        if len(sys.argv) > 1:
            app = SingleApplicationWithMessaging(sys.argv, key)
            if app.isRunning():
                print('app is already running')
                app.sendMessage(sys.argv[1])
                sys.exit(1)
        else:
            app = SingleApplicationWithMessaging(sys.argv, key)
            if app.isRunning():
                print('app is already running')
                app.sendMessage("focusWindow")
                sys.exit(1)
    else:
        app = QApplication(sys.argv)

    model = TorrentModel(app)
    controller = TorrentController(model)
    view = MainView(app, model, controller)
    process_args(model)
    if "windows" in platform.system().lower():
        app.messageAvailable.connect(handleMessage)

    app_exec = app.exec_()

    model.dispose()

    time.sleep(15)

    ThreadsManager.kill_all_threads()

    time.sleep(5)  # enough time to finish all the threads

    me = os.getpid()
    kill_proc_tree(me)

    sys.exit(app_exec)

    sys.exit(app.exec_())