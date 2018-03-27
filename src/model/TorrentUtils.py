def is_magnet_link(link):
    return "magnet:" in link


def set_file_priority(handle, file_index, priority):
    handle.file_priority(file_index, priority)


def set_file_priorities_for_start(handle):
    handle.paused = False
    info = handle.torrent_file()
    num_files = info.num_files()
    for i in range(0, num_files):
        set_file_priority(handle, i, 255)


def set_file_priorities_for_pause(handle):
    handle.paused = True
    info = handle.torrent_file()
    num_files = info.num_files()
    for i in range(0, num_files):
        set_file_priority(handle, i, 0)
