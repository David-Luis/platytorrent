from PyQt5.QtWidgets import *

from src.view.windows.AddLinkWindowView import AddLinkWindowView


class MenuBar(QMenuBar):
    def __init__(self, torrent_view, torrent_model, torrent_controller):
        super().__init__()

        self.torrent_view = torrent_view
        self.torrent_model = torrent_model
        self.torrent_controller = torrent_controller

        self.add_link_window_view = None

        file_menu = self.addMenu('&File')
        add_torrent = file_menu.addAction("Add Torrent...")
        add_magnet = file_menu.addAction("Add Magnet...")

        self.fetch_from_server = QAction("Fetch From Server", file_menu, checkable=True)
        self.fetch_from_server.setChecked(self.torrent_model.fetch_from_server)
        file_menu.addAction(self.fetch_from_server)
        file_menu.addSeparator()

        self.preselect_only_video_files = QAction("Preselect only video files", file_menu, checkable=True)
        self.preselect_only_video_files.setChecked(self.torrent_model.preselect_only_video_files)
        file_menu.addAction(self.preselect_only_video_files)
        file_menu.addSeparator()

        exit_action = file_menu.addAction("Exit")

        add_torrent.triggered.connect(self.__on_add_torrent)
        add_magnet.triggered.connect(self.__on_add_magnet)
        self.fetch_from_server.toggled.connect(self.__on_fetch_from_server)
        self.preselect_only_video_files.toggled.connect(self.__on_preselect_only_video_files)
        exit_action.triggered.connect(self.__on_exit)

    def __on_add_torrent(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "QFileDialog.getOpenFileName()", "",
                                                  "Torrent files (*.torrent)", options=options)
        if file_name:
            self.torrent_controller.add_torrent(file_name)

    def __on_add_magnet(self):
        self.add_link_window_view = AddLinkWindowView("Add Magnet", lambda link: self.__add_magnet(link))

    def __add_magnet(self, link):
        self.torrent_controller.add_magnet(link)

    def __on_fetch_from_server(self):
        self.torrent_controller.enable_fetch_from_server(self.fetch_from_server.isChecked())

    def __on_preselect_only_video_files(self):
        self.torrent_controller.enable_preselect_only_video_files(self.preselect_only_video_files.isChecked())

    def __on_exit(self):
        self.torrent_view.close()
