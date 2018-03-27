from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from src.view.windows.Window import Window
from src.view import ViewUtils
from src.model import Events


class DownloadTorrentWindowView(Window):
    def __init__(self, torrent_controller, torrent_model, torrent_handle):
        super().__init__()

        self.setModal(True)

        self.filled_torrent_info = False
        self.torrent_added = False

        self.torrent_controller = torrent_controller
        self.torrent_model = torrent_model
        self.torrent_model.subscribe(self)
        self.torrent_handle = torrent_handle

        self.main_layout = None
        self.lb_title = None
        self.lb_size = None
        self.layout_download_path = None
        self.le_download_path = None
        self.bt_save_path = None
        self.layout_buttons = None
        self.bt_start_torrent = None
        self.bt_cancel = None

        self.cb_files = []

        self.__init_ui()

    def reject(self):
        self.close()

    def closeEvent(self, evnt):
        if not self.torrent_added:
            self.torrent_controller.remove_torrent(self.torrent_handle)

    def close(self):
        self.torrent_model.unsubscribe(self)
        if not self.torrent_added:
            self.torrent_controller.remove_torrent(self.torrent_handle)

        super().close()

    def __init_ui(self):
        self.setWindowTitle("Torrent Info")

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.lb_title = QLabel("Title: ")
        self.main_layout.addWidget(self.lb_title)

        self.lb_size = QLabel("Size: ")
        self.main_layout.addWidget(self.lb_size)

        self.layout_download_path = QHBoxLayout()
        self.main_layout.addLayout(self.layout_download_path)

        self.le_download_path = QLineEdit(self.torrent_model.get_download_path())
        self.layout_download_path.addWidget(self.le_download_path)

        self.bt_save_path = QPushButton("...")
        self.bt_save_path.clicked.connect(self.__on_save_path_pressed)
        self.bt_save_path.setMaximumWidth(30)
        self.layout_download_path.addWidget(self.bt_save_path)

        self.__create_file_list()

        self.layout_buttons = QHBoxLayout()
        self.main_layout.addLayout(self.layout_buttons)

        self.bt_start_torrent = QPushButton("Ok")
        self.bt_start_torrent.clicked.connect(self.__on_start_torrent_click)
        self.layout_buttons.addWidget(self.bt_start_torrent)

        self.bt_cancel = QPushButton("Cancel")
        self.bt_cancel.clicked.connect(self.__on_cancel_torrent)
        self.layout_buttons.addWidget(self.bt_cancel)

        self.bt_start_torrent.setFocus()

        size = {'width': 600, 'height': 400}
        self.center_in_main_window(size)

        self.show()

    def __create_file_list(self):
        self.file_layout = QListWidget()
        self.scroll_list = QScrollArea()
        self.scroll_list.setWidgetResizable(True)
        self.scroll_list.setWidget(self.file_layout)
        self.main_layout.addWidget(self.scroll_list)

        self.file_layout.addItem("Loading Info...")

    def __add_element_to_file_list(self, file_index, file_name, text):
        item_list = QListWidgetItem()
        widget = QWidget()

        cb_download = QCheckBox(text)
        cb_download.file_index = file_index
        cb_download.file_name = file_name
        self.__set_default_selection_download(cb_download, file_name)
        self.cb_files.append(cb_download)

        widgetLayout = QHBoxLayout()
        widgetLayout.addWidget(cb_download)
        widgetLayout.addStretch()

        widgetLayout.setSizeConstraint(QLayout.SetFixedSize)
        widget.setLayout(widgetLayout)
        item_list.setSizeHint(widget.sizeHint())

        # Add widget to QListWidget funList
        self.file_layout.addItem(item_list)
        self.file_layout.setItemWidget(item_list, widget)

    def __set_default_selection_download(self, checkbox, file_name):
        if self.torrent_model.preselect_only_video_files:
            checkbox.setChecked(self.__is_video_file(file_name))
        else:
            checkbox.setChecked(True)

    def on_update_torrent(self, handle_list):
        if not self.filled_torrent_info:
            for handle in handle_list:
                if handle == self.torrent_handle:
                    self.__update_if_metadata_downloaded(handle)


    def __update_if_metadata_downloaded(self, handle):
        status = handle.status()
        progress = status.progress
        if progress == 1.0:
            self.filled_torrent_info = True
            self.__fill_torrent_info(handle)

    def __fill_torrent_info(self, handle):
        print("__fill_torrent_info")
        status = handle.status()
        torrent_file = handle.torrent_file()

        self.lb_title.setText("Title: " + status.name)
        self.lb_size.setText("Size: " + ViewUtils.get_formatted_size(torrent_file.total_size()))
        self.file_layout.clear()
        files = torrent_file.files()
        num_files = files.num_files()
        for i in range(0, num_files):
            file_entry = files.at(i)
            if num_files > 1:
                file_name = file_entry.path.replace(status.name, "", 1).replace("\\", "")
            else:
                file_name = file_entry.path
            file_size = files.file_size(i)
            self.__add_element_to_file_list(i, file_name, file_name + " - " + ViewUtils.get_formatted_size(file_size))

    def notify(self, event_type, args):
        if event_type == Events.UPDATE_TORRENT:
            self.on_update_torrent(args)

    def __on_save_path_pressed(self):
        save_path = str(QFileDialog.getExistingDirectory(self,
                                                         "Select Directory",
                                                         self.torrent_model.get_download_path()))
        if save_path:
            self.torrent_controller.change_save_path(save_path)
            self.le_download_path.setText(self.torrent_model.get_download_path())

    def __on_start_torrent_click(self):

        index_files_selected = self.__get_index_files_selected()
        if index_files_selected:
            if len(index_files_selected) == 1:
                self.__remove_folder_from_download_path(self.torrent_handle, self.cb_files[index_files_selected[0]].file_name, index_files_selected[0])

            self.__set_files_to_download()

        if index_files_selected or not self.filled_torrent_info:
            self.torrent_added = True
            self.torrent_controller.start_torrent(self.torrent_handle)

        self.close()

    def __get_index_files_selected(self):
        files_selected = []
        for checkbox in self.cb_files:
            if checkbox.isChecked():
                files_selected.append(checkbox.file_index)

        return files_selected

    def __remove_folder_from_download_path(self, handle, file_name, file_index):
        print("set file name " + file_name)
        handle.rename_file(file_index, file_name)

    def __set_files_to_download(self):
        for checkbox in self.cb_files:
            self.torrent_controller.set_file_to_download(self.torrent_handle, checkbox.file_index, checkbox.isChecked())

    def __on_cancel_torrent(self):
        self.close()

    def __is_video_file(self, file_name):
        video_extensions = ['avi', 'mkv', 'wmv', 'mp4', 'mpg', '3gp', 'mov']
        for video_extension in video_extensions:
            if file_name.endswith(video_extension):
                return True

        return False
