from PyQt5.QtWidgets import *

from src.view.windows.Window import Window


class AddLinkWindowView(Window):
    def __init__(self, title, callback_link):
        super().__init__()

        self.setModal(True)
        self.title = title
        self.callback_link = callback_link
        self.main_layout = None
        self.le_link = None
        self.bt_ok = None

        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle(self.title)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.le_link = QLineEdit()
        clipboard = QApplication.clipboard()
        if clipboard.mimeData().hasText():
            self.le_link.setText(clipboard.mimeData().text())

        self.bt_ok = QPushButton("Ok")
        self.main_layout.addWidget(self.le_link)
        self.main_layout.addWidget(self.bt_ok)
        self.bt_ok.clicked.connect(self.__on_ok_clicked)

        size = {'width': 300, 'height': 100}
        self.center_in_main_window(size)

        self.show()

    def __on_ok_clicked(self):
        self.callback_link(self.le_link.text())
        self.close()

