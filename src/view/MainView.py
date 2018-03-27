from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

from src.model import Events
from src.view.MenuBar import MenuBar
from src.view.windows.Window import Window
from src.view.TorrentListView import TorrentListView
from src.view import ViewUtils
from src.view.windows.DownloadTorrentWindowView import DownloadTorrentWindowView

import time

import ctypes
import platform

class MainView(QMainWindow):
    def __init__(self, app, torrent_model, torrent_controller):
        super().__init__()

        self.torrent_model = torrent_model
        self.torrent_model.subscribe(self)
        self.torrent_controller = torrent_controller
        Window.main_window = self
        self.app = app

        self.__set_app__icon()

        self.main_layout = None
        self.torrent_list_view = None
        self.download_torrent_window_view = None
        
        self.__init_ui()
        self.__update_general_info()
        self.setMenuBar(MenuBar(self, self.torrent_model, self.torrent_controller))

    def focusWindow(self):
        self.raise_()
        self.activateWindow()

    def __init_ui(self):
        self.setGeometry(300, 300, 1000, 600)
        self.setWindowTitle('Platytorrent')

        self.setCentralWidget(QWidget())
        self.main_layout = QVBoxLayout()
        self.centralWidget().setLayout(self.main_layout)

        self.torrent_list_view = TorrentListView(self.torrent_controller)
        self.main_layout.addWidget(self.torrent_list_view)

        self.status_bar_info = QLabel()
        self.statusBar().addPermanentWidget(self.status_bar_info)

        self.show()

    def __set_app__icon(self):
        app_icon = QIcon()
        app_icon.addFile('./icons/icon_16.png', QSize(16, 16))
        app_icon.addFile('./icons/icon_24.png', QSize(24, 24))
        app_icon.addFile('./icons/icon_32.png', QSize(32, 32))
        app_icon.addFile('./icons/icon_48.png', QSize(48, 48))
        app_icon.addFile('./icons/icon_256.png', QSize(256, 256))
        self.app.setWindowIcon(app_icon)

        # this is needed to show the icon in windows task bar
        if "windows" in platform.system().lower():
            myappid = 'platys.platytorrent.subproduct.version'  # arbitrary string
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    def __update_general_info(self):
        download_rate = self.torrent_model.get_total_download_rate()
        upload_rate = self.torrent_model.get_total_upload_rate()
        msg = "Download: " + ViewUtils.get_formatted_speed(download_rate) + " Upload: " + ViewUtils.get_formatted_speed(upload_rate)
        self.status_bar_info.setText(msg)

    def notify(self, event_type, args):
        self.event_type = event_type
        self.args = args
        self.__process_event(event_type, args)


    def __process_event(self, event_type, args):
        print(event_type)
        if event_type == Events.ADDED_TORRENT:
            self.download_torrent_window_view = DownloadTorrentWindowView(self.torrent_controller, self.torrent_model, args)
        if event_type == Events.STARTED_TORRENT:
            self.torrent_list_view.add_torrent(args)
        if event_type == Events.UPDATE_TORRENT:
            self.torrent_list_view.update_torrents_info(args)
            self.__update_general_info()
        if event_type == Events.REMOVED_TORRENT:
            self.torrent_list_view.remove_torrent(args)
        if event_type == Events.PAUSED_TORRENT:
            self.torrent_list_view.pause_torrent(args)
        if event_type == Events.RESUME_TORRENT:
            self.torrent_list_view.resume_torrent(args)

