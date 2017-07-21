from datetime import datetime
from threading import Thread
import psutil
import time


old_status = None
current_io_status = None
old_time = 0


# convert bytes to gigabytes
def gb_convert(byts):
    return byts / 1024 / 1024 / 1024


# loop every 1 second to update I/O records
def update_io():
    global old_status
    global current_io_status
    global old_time
    while True:
        # get current status
        new_status = psutil.disk_io_counters(perdisk=False)

        # get 1 second difference in I/O format
        interval = (datetime.now() - old_time).total_seconds()
        if new_status.write_bytes - old_status.write_bytes == 0:
            current_io_status = 0.0
        else:
            current_io_status = (new_status.write_bytes - old_status.write_bytes) / interval

        # give current I/O to old I/O for another math problem
        old_status = new_status
        old_time = datetime.now()

        time.sleep(1)


class Disk:
    def __init__(self):
        global old_status
        global old_time
        # initial info
        old_status = psutil.disk_io_counters(perdisk=False)
        old_time = datetime.now()

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
            used = round(gb_convert(specs.used), 1)
            total = round(gb_convert(specs.total), 1)

            disks.append(Device(dsk.mountpoint, specs.percent, used, total))

        # list of disks
        return disks

    # get disk I/O
    def get_disk_io(self):
        global current_io_status

        # current disk I/O
        return current_io_status


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
