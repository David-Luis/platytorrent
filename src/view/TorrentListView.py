from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from src.view.widgets.TorrentListElementLayout import TorrentListElementLayout


class TorrentListView(QWidget):
    def __init__(self, torrent_controller):
        super().__init__()

        self.torrent_controller = torrent_controller
        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.torrent_layout = QListWidget()
        self.scroll_list = QScrollArea()
        self.scroll_list.setWidgetResizable(True)
        self.scroll_list.setWidget(self.torrent_layout)
        self.main_layout.addWidget(self.scroll_list)

        self.torrent_list_elements = {}

    def add_torrent(self, handle):
        if not self.have_handle(handle):
            list_element = TorrentListElementLayout(self.torrent_controller, handle)
            item_list = QListWidgetItem()
            item_list.setSizeHint(list_element.sizeHint())
            list_element.listWidgetItem = item_list

            self.torrent_layout.addItem(item_list)
            self.torrent_layout.setItemWidget(item_list, list_element)
            self.torrent_list_elements[handle.torrent_id] = list_element

    def remove_torrent(self, handle):
        if self.have_handle(handle):
            torrent_list_element = self.torrent_list_elements[handle.torrent_id]
            self.torrent_list_elements[handle.torrent_id] = None
            self.torrent_layout.removeItemWidget(torrent_list_element.listWidgetItem)

    def pause_torrent(self, handle):
        if self.have_handle(handle):
            torrent_list_element = self.torrent_list_elements[handle.torrent_id]
            torrent_list_element.pause_torrent()

    def resume_torrent(self, handle):
        if self.have_handle(handle):
            torrent_list_element = self.torrent_list_elements[handle.torrent_id]
            torrent_list_element.resume_torrent()

    def update_torrents_info(self, handle_list):
        for handle in handle_list:
            if self.have_handle(handle):
                torrent_list_element = self.torrent_list_elements[handle.torrent_id]
                torrent_list_element.update_torrent_info()

    def have_handle(self, handle):
        return self.torrent_list_elements and handle.torrent_id in self.torrent_list_elements and self.torrent_list_elements[handle.torrent_id] != None

