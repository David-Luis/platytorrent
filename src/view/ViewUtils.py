def delete_items_of_layout(layout):
    if layout is not None:
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
            else:
                delete_items_of_layout(item.layout())

def get_formatted_time(value):
    if value / 3600 > 1:  # if more than 1000 KB
        return str(int(value / 3600)) + "h"
    elif value / 60 > 1:  # if more than 1000 KB
        return str(int(value / 60)) + "m"
    else:
        return str(int(value)) + "s"


def get_formatted_percentage(value):
    return "{0:.2f}%".format(value * 100)


def get_formatted_size(value):
    if value / 1000000 > 1000:  # if more than 1000 MB
        return "{0:.2f} GB".format(value / 1000000000)
    elif value / 1000 > 1000:  # if more than 1000 KB
        return "{0:.2f} MB".format(value / 1000000)
    else:
        return "{0:.2f} KB".format(value / 1000)


def get_formatted_speed(value):
    if value / 1000 > 1000:  # if more than 1000 KB
        return "{0:.2f} MB/s".format(value / 1000000)
    else:
        return "{0:.2f} KB/s".format(value / 1000)