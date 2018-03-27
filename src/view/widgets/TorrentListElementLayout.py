from PyQt5.QtWidgets import *
from playsound import playsound

from src.view import ViewUtils
from src.view.windows.WindowConfirmationWithCheckboxView import WindowConfirmationWithCheckboxView

import sys
import os

class TorrentListElementLayout(QWidget):
    def __init__(self, torrent_controller, handle):
        super().__init__()

        self.torrent_controller = torrent_controller
        self.handle = handle
        self.main_layout = QHBoxLayout()
        self.setLayout(self.main_layout)

        self.lb_info = QLabel()
        self.main_layout.addWidget(self.lb_info)

        self.lb_pause_resume = QPushButton("Pause")
        self.main_layout.addWidget(self.lb_pause_resume)
        self.lb_pause_resume.clicked.connect(self.on_pause_resume_pressed)

        self.lb_remove_torrent = QPushButton("X")
        self.main_layout.addWidget(self.lb_remove_torrent)
        self.lb_remove_torrent.clicked.connect(self.on_remove_torrent)

        self.finished = False
        self.paused = False
        self.hack_play_complete_sound = 0 #hack: sometimes we get one update with 100% and files ready

    def update_torrent_info(self):
        status = self.handle.status()
        name = status.name
        progress = ViewUtils.get_formatted_percentage(status.progress)
        download_rate = ViewUtils.get_formatted_speed(status.download_rate)
        upload_rate = ViewUtils.get_formatted_speed(status.upload_rate)
        total_size = "-"
        remaining_time = "-"
        file = self.handle.torrent_file()
        if file:
            total_size = ViewUtils.get_formatted_size(file.total_size())
            remaining_size = file.total_size() - status.progress * file.total_size()
            if status.download_rate > 0:
                remaining_time = ViewUtils.get_formatted_time(remaining_size / status.download_rate)

        self.lb_info.setText(name + "  " + progress + " download: " + download_rate + " upload: " +
                             upload_rate + " files Size: " + total_size + " estimated time: " +
                             remaining_time)

        if not self.finished and status.progress == 1.0 and file:
            if self.hack_play_complete_sound == 1:
                print("PLAYING COMPLETE SOUND")
                self.finished = True
                playsound("complete.wav")
            else:
                self.hack_play_complete_sound = 1

    def on_pause_resume_pressed(self):
        if self.paused:
            self.torrent_controller.resume_torrent(self.handle)
        else:
            self.torrent_controller.pause_torrent(self.handle)

    def pause_torrent(self):
        self.lb_pause_resume.setText("Resume")
        self.paused = True

    def resume_torrent(self):
        self.lb_pause_resume.setText("Pause")
        self.paused = False

    def on_remove_torrent(self):
        self.window_confirmation = \
            WindowConfirmationWithCheckboxView("Delete torrent",
                                               "Are you sure you want to delete this torrent?",
                                               "Delete files",
                                               lambda delete_files: self.remove_torrent(delete_files))

    def remove_torrent(self, delete_files):
        try:
            files = None
            info = self.handle.torrent_file()
            if info:
                files = info.files()
            self.torrent_controller.remove_torrent(self.handle)
            if files and delete_files:
                for i in range(0, files.num_files()):
                    os.remove(self.handle.save_path + "/" + files.file_path(i))
        except:
            print("remove_torrent")
            print(sys.exc_info()[0])
            print(sys.exc_info()[1])

    def remove_widgets(self):
        ViewUtils.delete_items_of_layout(self)



