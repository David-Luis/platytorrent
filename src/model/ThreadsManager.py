from PyQt5.QtCore import *

threads = []

import time

import threading

class SimpleThread(QThread):
    signal_target = pyqtSignal()

    def __init__(self, parent, target, sleep_time):
        super().__init__()
        QThread.__init__(self, parent)
        self.signal_target.connect(target)
        self.target = target
        self.exit = False
        self.sleep_time = sleep_time

    def run(self):
        while not self.exit:
            #self.target()
            self.signal_target.emit()
            time.sleep(self.sleep_time)


def start_main_thread(parent, target_function, sleep_time):
    thread = SimpleThread(target=target_function, parent=parent, sleep_time=sleep_time)
    threads.append(thread)
    thread.start()

    return thread

def start_thread(target_function):
    thread = threading.Thread(target=target_function)
    thread.exit = False
    threads.append(thread)
    thread.start()

def kill_all_threads():
    for thread in threads:
        thread.exit = True

