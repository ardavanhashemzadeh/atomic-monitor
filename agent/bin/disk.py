from datetime import datetime
from threading import Thread
import psutil
import time


old_io = 0.00
current_io = 0
timer = 0


# convert bytes to gigabytes
def gb_convert(byts):
    return byts / 1024 / 1024 / 1024


# loop every .2 seconds to update I/O records
def update_io():
    global old_io
    global current_io
    global timer
    while True:
        # get current status
        new_io = psutil.disk_io_counters(perdisk=False)

        # do math
        interval = (datetime.now() - timer).total_seconds()
        if new_io.write_bytes - old_io.write_bytes == 0:
            current_io = 0.0
        else:
            current_io = (new_io.write_bytes - old_io.write_bytes) / interval

        # give current I/O to old I/O for another math problem
        old_io = new_io
        timer = datetime.now()

        time.sleep(0.2)


class Disk:
    def __init__(self):
        global old_io
        global timer
        # initial info
        old_io = psutil.disk_io_counters(perdisk=False)
        timer = datetime.now()

        # start thread process
        thd = Thread(target=update_io)
        thd.daemon = True
        thd.start()

    # get disk usage
    def get_disks(self):
        status = psutil.disk_partitions()

        # goes through the list of disks & retrieve usage
        disks = list()
        for dsk in status:
            specs = psutil.disk_usage(dsk.mountpoint)

            # convert bytes to gigabytes
            used = round(gb_convert(specs.used), 0)
            total = round(gb_convert(specs.total), 0)

            disks.append(Device(dsk.mountpoint, specs.percent, used, total))

        # list of disks
        return disks

    # get disk I/O
    def get_disk_io(self):
        global current_io

        # current disk I/O
        return current_io


class Device:
    def __init__(self, _name, _percent, _used, _total):
        self.name = _name
        self.percent = _percent
        self.used = _used
        self.total = _total

    def get_name(self):
        return self.name

    def get_percent(self):
        return self.percent

    def get_used(self):
        return self.used

    def get_total(self):
        return self.total
