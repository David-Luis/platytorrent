from PyQt5.QtWidgets import *


class Window(QDialog):
    main_window = None

    def __init__(self):
        super().__init__()

    def center_in_main_window(self, size):
        x = Window.main_window.frameGeometry().x()
        y = Window.main_window.frameGeometry().y()
        width = Window.main_window.frameGeometry().width()
        height = Window.main_window.frameGeometry().height()

        center = {'x': x + width / 2, 'y': y + height / 2}

        self.setGeometry(center['x'] - size['width'] / 2,
                         center['y'] - size['height'] / 2,
                         size['width'],
                         size['height'])


