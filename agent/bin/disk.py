from datetime import datetime
from threading import Thread
import psutil
import time


# convert bytes to gigabytes
def gb_convert(byts):
    return byts / 1024 / 1024 / 1024


class Disk:
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


class Device:
    def __init__(self, _name, _percent, _used, _total):
        self.name = _name
        self.percent = _percent
        self.used = _used
        self.total = _total
