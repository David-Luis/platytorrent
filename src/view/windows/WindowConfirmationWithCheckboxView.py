from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from src.view.windows.Window import Window


class WindowConfirmationWithCheckboxView(Window):
    def __init__(self, title, text, checkbox_text, callback_yes):
        super().__init__()

        self.setModal(True)
        self.title = title
        self.text = text
        self.checkbox_text = checkbox_text
        self.callback_yes = callback_yes
        self.main_layout = None
        self.lb_link = None
        self.bt_ok = None

        self.__init_ui()

    def __init_ui(self):
        self.setWindowTitle(self.title)

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.lb_link = QLabel(self.text)
        self.lb_link.setAlignment(Qt.AlignCenter)
        self.main_layout.addWidget(self.lb_link)

        self.buttons_layout = QHBoxLayout()
        self.buttons_layout.setSpacing(20)
        self.main_layout.addLayout(self.buttons_layout)

        self.cb_option = QCheckBox(self.checkbox_text)
        self.main_layout.addWidget(self.cb_option)

        self.bt_ok = QPushButton("Ok")
        self.buttons_layout.addWidget(self.bt_ok)
        self.bt_ok.clicked.connect(self.__on_ok_clicked)

        self.bt_cancel = QPushButton("Cancel")
        self.buttons_layout.addWidget(self.bt_cancel)
        self.bt_cancel.clicked.connect(self.close)

        self.bt_ok.setFocus()

        size = {'width': 250, 'height': 100}
        self.center_in_main_window(size)

        self.show()

    def __on_ok_clicked(self):
        self.callback_yes(self.cb_option.isChecked())
        self.close()

