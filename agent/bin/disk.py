import datetime
import psutil
import time


def gb_convert(byts):
    return byts / 1024 / 1024 / 1024


class Disk:
    # get disk usage
    def get_disks(self):
        status = psutil.disk_partitions()

        # goes through the list of disks & retrieve usage
        disks = list()
        for dsk in status:
            specs = psutil.disk_usage(dsk.device)

            # convert bytes to gigabytes
            used = gb_convert(specs.used)
            total = gb_convert(specs.total)

            disks.append(Device(dsk.device, specs.percent, used, total))

        # list of disks
        return disks

    # get disk I/O
    def get_disk_io(self):
        disk_counters = psutil.disk_io_counters(perdisk=False)
        counter_ts = datetime.datetime.now()
        time.sleep(0.2)

        now = datetime.datetime.now()
        interval = (now - counter_ts).total_seconds()

        disk = psutil.disk_io_counters(perdisk=False)
        io = (disk.write_bytes - disk_counters.write_bytes) / interval

        return io


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
