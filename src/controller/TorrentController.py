from src.model import TorrentUtils

import threading

class TorrentController:
    def __init__(self, model_torrent):
        self.model_torrent = model_torrent

    def change_save_path(self, path):
        self.model_torrent.set_save_path(path)
        self.model_torrent.save_user_options()

    def add_torrent(self, path, should_notify=True):
        self.model_torrent.add_torrent(path, should_notify=should_notify)

    def add_magnet(self, link, should_notify=True):
        self.model_torrent.add_magnet(link, should_notify=should_notify)

    def add_magnet_or_torrent(self, link, should_notify=True):
        if TorrentUtils.is_magnet_link(link):
            self.add_magnet(link, should_notify)
        else:
            self.add_torrent(link, should_notify)

    def enable_fetch_from_server(self, value):
        lock = threading.Lock()
        with lock:
            self.model_torrent.fetch_from_server = value
            self.model_torrent.server_torrent_fetcher.resume_or_pause(value)
            self.model_torrent.save_user_options()

    def enable_preselect_only_video_files(self, value):
        self.model_torrent.preselect_only_video_files = value
        self.model_torrent.save_user_options()

    def start_torrent(self, handle):
        self.model_torrent.start_torrent(handle)

    def remove_torrent(self, handle):
        self.model_torrent.remove_torrent(handle)

    def pause_torrent(self, handle):
        self.model_torrent.pause_torrent(handle)

    def resume_torrent(self, handle):
        self.model_torrent.resume_torrent(handle)

    def set_file_to_download(self, torrent_handle, file_entry, should_download):
        if should_download:
            TorrentUtils.set_file_priority(torrent_handle, file_entry, 255)
        else:
            TorrentUtils.set_file_priority(torrent_handle, file_entry, 0)



