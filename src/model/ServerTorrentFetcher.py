from src.model import TorrentUtils
from src.model import ThreadsManager

from PyQt5.QtCore import *
from PyQt5.QtWidgets import *

import threading

import time
import requests
import sys


class ServerTorrentFetcher(QWidget): #needs to be a qt object to use sygnals
    def __init__(self, torrent_model, app):
        super().__init__()
        self.thread_update = None
        self.torrent_model = torrent_model
        self.config_path = "server_config.ini"

        self.app = app
        self.enable_fetch = False
        self.started_thread = False
        self.downloaded_torrents = []
        self.pause_cond = threading.Condition(threading.Lock())

        if torrent_model.fetch_from_server:
            self.__start_fetching_thread()

    def resume_or_pause(self, enable):
        lock = threading.Lock()
        with lock:
            if self.torrent_model.fetch_from_server and not self.started_thread:
                self.__start_fetching_thread()
            elif not enable:
                self.started_thread = False

    def __start_fetching_thread(self):
        self.started_thread = True
        self.thread_update = ThreadsManager.start_thread(target_function=self.__fetch_server_thread)

    def __fetch_server_thread(self):
        while self.torrent_model.fetch_from_server:
            self.fetch_from_server()
            time.sleep(30)

        self.started_thread = False

    def fetch_from_server(self):
        self.list_of_torrents = []
        with open(self.config_path) as f:
            content = f.readlines()
            for torrent in content:
                r = requests.get(torrent)
                print("- " + r.text)
                for line in r.text.splitlines():
                    if line not in self.downloaded_torrents:
                        self.downloaded_torrents.append(line)
                        self.list_of_torrents.append(line)

        lock = threading.Lock()
        with lock:
            self.torrent_model.pending_torrents_to_add = self.list_of_torrents
            self.list_of_torrents = []

