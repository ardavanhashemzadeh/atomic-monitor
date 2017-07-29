from datetime import datetime
from threading import Thread
import psutil
import time


old_status = None
current_nic_status = None


# convert bytes to kilobytes
def bytes_to_kb(byts):
    return byts / 1024


# loop every second to update records
def update_nics():
    global old_status
    global current_nic_status
    while True:
        # get current net status
        new_stats = psutil.net_io_counters(pernic=True)

        # get 1 second difference in KB
        current_nic_status = list()
        nic_names = list()
        for nic in old_status.keys():
            nic_names.append(nic)
        for i in range(0, len(old_status)):
            diff_sent = round(bytes_to_kb(new_stats[nic_names[i]].bytes_sent - old_status[nic_names[i]].bytes_sent), 3)
            diff_recv = round(bytes_to_kb(new_stats[nic_names[i]].bytes_recv - old_status[nic_names[i]].bytes_recv), 3)

            current_nic_status.append(NIC(nic_names[i], diff_sent, diff_recv))

        old_status = new_stats

        time.sleep(1)


class Network:
    def __init__(self):
        global old_status

        # initial list
        old_status = psutil.net_io_counters(pernic=True)

        # start thread process
        thd = Thread(target=update_nics)
        thd.daemon = True
        thd.start()

    # retrieve NICs update
    def get_nic_status(self):
        global current_nic_status

        # NICs 
        return current_nic_status


class NIC:
    def __init__(self, _name, _sent, _recv):
        self.name = _name
        self.sent = _sent
        self.recv = _recv
