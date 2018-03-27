from src.model import Events
from src.model import TorrentUtils
from src.model import ThreadsManager
from src.model.ServerTorrentFetcher import ServerTorrentFetcher

import configparser

import libtorrent as lt
import time
import threading

import sys
import os
from sys import platform
from pathlib import Path
from PyQt5.QtCore import *


class TorrentModel(QObject):
    next_torrent_id = 0
    config_file_path = str(Path.home()) + "/.platytorrent/"
    config_file_name = "config.ini"

    def __init__(self, app):
        super().__init__()
        self.observers = []
        self.app = app

        self.save_path = (str(Path.home()) + "/Downloads").replace("\\", "/")
        self.fetch_from_server = False
        self.remove_torrent_finish_when_fetch_from_server = True
        self.preselect_only_video_files = True

        self.upload_limit = 50 * 1000  # 100 kb/s

        self.pending_torrents_to_add = []
        self.list_of_pending_starting_handles = []
        self.list_of_pending_pause_handles = []
        self.current_started_handles = []
        self.torrent_handlers = []

        self.load_user_options()
        self.save_user_options()

        self.start_torrent_thread()
        self.server_torrent_fetcher = ServerTorrentFetcher(self, app)

    def dispose(self):
        self.__save_resume_data()

    def start_torrent_thread(self):
        self.ses = lt.session()
        self.ses.listen_on(6881, 6891)
        self.thread_update = ThreadsManager.start_main_thread(self.app, self.__update, 1.0)

    def save_user_options(self):
        try:
            if not os.path.exists(TorrentModel.config_file_path):
                os.makedirs(TorrentModel.config_file_path)
            if not os.path.exists(TorrentModel.config_file_path+TorrentModel.config_file_name):
                with open(TorrentModel.config_file_path+TorrentModel.config_file_name, 'w'): pass

            print("FETCH FROM SERVER: " + str(self.fetch_from_server))

            config = configparser.ConfigParser()
            config['USER'] = {'download_path': self.save_path,
                              'fetch_from_server': str(self.fetch_from_server),
                              'remove_torrent_finish_when_fetch_from_server': str(self.remove_torrent_finish_when_fetch_from_server),
                              'preselect_only_video_files': str(self.preselect_only_video_files)
                              }

            with open(TorrentModel.config_file_path+TorrentModel.config_file_name, 'w') as configfile:
                config.write(configfile)
        except:
            print("save_user_options")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def load_user_options(self):
        config = configparser.ConfigParser()
        config.read(TorrentModel.config_file_path + TorrentModel.config_file_name)

        if 'USER' in config:
            if 'download_path' in config['USER']:
                self.save_path = config['USER']['download_path']
            if 'fetch_from_server' in config['USER']:
                self.fetch_from_server = config['USER']['fetch_from_server'] == "True"
            if "remove_torrent_finish_when_fetch_from_server" in config['USER']:
                self.remove_torrent_finish_when_fetch_from_server =  config['USER']['remove_torrent_finish_when_fetch_from_server'] == "True"
            if "preselect_only_video_files" in config['USER']:
                self.preselect_only_video_files = config['USER']['preselect_only_video_files']  == "True"

    def set_save_path(self, path):
        self.save_path = path

    def add_torrent(self, path, should_notify=True):
        e = lt.bdecode(open(path, 'rb').read())
        info = lt.torrent_info(e)

        params = {'save_path': self.save_path,
                  'storage_mode': lt.storage_mode_t.storage_mode_sparse,
                  'file_priorities': [0] * 1000,
                  'ti': info}

        handle = self.ses.add_torrent(params)
        if not self.__is_torrent_already_in_list(handle):
            self.set_handle_properties(handle)
            if should_notify:
                self.__notify_torrent_added(handle)
            return handle

        return None

    def add_magnet(self, link, should_notify=True):
        if not TorrentUtils.is_magnet_link(link):
            return None

        try:
            params = {'save_path': self.save_path,
                      'file_priorities': [0] * 1000,
                      'storage_mode': lt.storage_mode_t.storage_mode_sparse}

            handle = lt.add_magnet_uri(self.ses, link, params)
            if not self.__is_torrent_already_in_list(handle):
                self.set_handle_properties(handle)
                if should_notify:
                    self.__notify_torrent_added(handle)
                return handle

            return None

        except:
            print("add_magnet")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])
            return None

    def add_magnet_or_torrent(self, link, should_notify=True):
        if TorrentUtils.is_magnet_link(link):
            return self.add_magnet(link, should_notify)
        else:
            return self.add_torrent(link, should_notify)

    def set_handle_properties(self, handle):
        handle.torrent_id = TorrentModel.next_torrent_id
        TorrentModel.next_torrent_id += 1
        handle.save_path = self.save_path
        handle.remove_when_finish = True
        handle.paused = True
        handle.set_upload_limit(self.upload_limit)

        self.torrent_handlers.append(handle)

    def start_torrent(self, handle, should_notify=True):
        try:
            if handle not in self.current_started_handles:
                self.current_started_handles.append(handle)
                if not handle.torrent_file():
                    self.list_of_pending_starting_handles.append(handle)

                if should_notify:
                    self.__notify_torrent_started(handle)

        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def remove_torrent(self, handle):
        try:
            if handle in self.torrent_handlers:
                self.torrent_handlers.remove(handle)
            if handle in self.list_of_pending_starting_handles:
                self.list_of_pending_starting_handles.remove(handle)
            if handle in self.current_started_handles:
                self.current_started_handles.remove(handle)
            self.__notify_torrent_removed(handle)
            self.ses.remove_torrent(handle)
        except:
            print("remove_torrent")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def pause_torrent(self, handle):
        try:
            if handle.torrent_file():
                TorrentUtils.set_file_priorities_for_pause(handle)
            else:
                self.list_of_pending_pause_handles.append(handle)
            self.__notify_torrent_paused(handle)
        except:
            print("pause_torrent")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def resume_torrent(self, handle):
        self.start_torrent(handle)
        self.__notify_torrent_resume(handle)

    def subscribe(self, subscriber):
        self.observers.append(subscriber)

    def unsubscribe(self, subscriber):
        self.observers.remove(subscriber)

    def get_total_download_rate(self):
        total_download_rate = 0
        for handle in self.torrent_handlers:
            total_download_rate += handle.status().download_rate

        return total_download_rate

    def get_total_upload_rate(self):
        total_upload_rate = 0
        for handle in self.torrent_handlers:
            total_upload_rate += handle.status().upload_rate

        return total_upload_rate

    def __update(self):
        self.__check_resume_save_data()
        self.__update_torrents_info()
        self.__check_if_can_pause_pending_torrents()
        self.__check_if_can_start_pending_torrents()
        self.__check_remove_when_finish()
        self.__check_pending_torrents_to_add()

    def __update_torrents_info(self):
        try:
            for handle in self.torrent_handlers:
                status = handle.status()
                print('%.2f%% complete (down: %.1f kb/s up: %.1f kB/s peers: %d) %s' %
                      (status.progress * 100, status.download_rate / 1000, status.upload_rate / 1000,
                       status.num_peers, 0))

            self.__notify_torrents_info(Events.UPDATE_TORRENT)
        except:
            print("__update_torrents_info")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def __check_remove_when_finish(self):
        try:
            needs_to_finish_torrents = []
            for handle in self.torrent_handlers:
                if handle.remove_when_finish and handle.status().progress == 1.0 and not handle.paused:
                    needs_to_finish_torrents.append(handle)

            for handle in needs_to_finish_torrents:
                self.remove_torrent(handle)

        except:
            print("__check_remove_when_finish")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def __check_if_can_start_pending_torrents(self):
        started_torrents = []
        for handle in self.list_of_pending_starting_handles:
            if handle.torrent_file():
                TorrentUtils.set_file_priorities_for_start(handle)
                started_torrents.append(handle)

        for handle in started_torrents:
            self.list_of_pending_starting_handles.remove(handle)

    def __check_if_can_pause_pending_torrents(self):
        paused_torrents = []
        for handle in self.list_of_pending_pause_handles:
            if handle.torrent_file():
                TorrentUtils.set_file_priorities_for_pause(handle)
                paused_torrents.append(handle)

        for handle in paused_torrents:
            self.list_of_pending_pause_handles.remove(handle)

    def __notify(self, event_type, info):
        for observer in self.observers:
            observer.notify(event_type, info)

    def __notify_torrent_added(self, handle):
        self.__notify(Events.ADDED_TORRENT, handle)

    def __notify_torrent_started(self, handle):
        self.__notify(Events.STARTED_TORRENT, handle)

    def __notify_torrents_info(self, event):
        try:
            if self.torrent_handlers:
                self.__notify(event, self.torrent_handlers)
        except:
            print("__notify_torrents_info")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def __notify_torrent_removed(self, handle):
        self.__notify(Events.REMOVED_TORRENT, handle)

    def __notify_torrent_paused(self, handle):
        self.__notify(Events.PAUSED_TORRENT, handle)

    def __notify_torrent_resume(self, handle):
        self.__notify(Events.RESUME_TORRENT, handle)

    def get_download_path(self):
        return self.save_path

    def __is_torrent_already_in_list(self, handle):
        return handle in self.torrent_handlers or\
               handle in self.list_of_pending_starting_handles or\
               handle in self.current_started_handles

    def __save_resume_data(self):
        for handle in self.torrent_handlers:
            handle.save_resume_data()

    def __check_pending_torrents_to_add(self):
        lock = threading.Lock()
        with lock:
            for torrent in self.pending_torrents_to_add:
                handle = self.add_magnet_or_torrent(torrent, should_notify=False)
                if handle:
                    handle.remove_when_finish = self.remove_torrent_finish_when_fetch_from_server
                    self.start_torrent(handle, should_notify=True)

            self.pending_torrents_to_add = []

    def __check_resume_save_data(self):
        return
        try:
            alerts = self.ses.pop_alerts()
            for a in alerts:
                if type(a) == lt.save_resume_data_alert:
                    print(a)
                    data = lt.bencode(a.resume_data)
                    h = a.handle
                    status = h.status()
                    if h in self.torrent_handlers:
                        open(os.path.join(TorrentModel.config_file_path, status.name + '.fastresume'), 'wb').write(data)
        except:
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])


