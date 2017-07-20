from datetime import datetime
from threading import Thread
import psutil
import time


previous_nics = list()
interval = 0


# convert bytes to kilobytes
def bytes_to_kb(byts):
    return byts / 1024


# loop every second to update records
def update_nics():
    global previous_nics
    global interval
    while True:
        # get current status
        now_nics = psutil.net_io_counters(pernic=True)

        for i in range(0, len(previous_nics)):
            name = previous_nics[0]




        for net in previous_nics.keys():
            diff_sent =


        # get current status
        nic_list = psutil.net_io_counters(pernic=True)
        for net in nic_list.keys():
            new_nics.append(NIC(net, nic_list[net].bytes_sent, nic_list[net].bytes_recv))

        # do math to get change in 1 second difference
        nics = list()
        for i in range(0, len(old_nics)):
            diff_sent = round(bytes_to_kb(new_nics[i].get_sent() - old_nics[i].get_sent()), 3)
            diff_recv = round(bytes_to_kb(new_nics[i].get_recv() - old_nics[i].get_recv()), 3)

            nics.append(NIC(old_nics[i].get_name(),
                            diff_sent,
                            diff_recv))

        # give current NICs to old list for another math problem
        old_nics = new_nics

        time.sleep(0.2)


class Network:
    def __init__(self):
        global previous_nics
        global interval
        # initial list
        previous_nics = psutil.net_io_counters(pernic=True)
        interval = datetime.now()

        # start thread process
        thd = Thread(target=update_nics)
        thd.daemon = True
        thd.start()

    # retrieve NICs update
    def get_nic_status(self):
        global nics

        # NICs w/ num bytes sent/received
        return nics


class NIC:
    def __init__(self, _name, _sent, _recv):
        self.name = _name
        self.sent = _sent
        self.recv = _recv

    # name of NIC
    def get_name(self):
        return self.name

    # num of bytes sent
    def get_sent(self):
        return self.sent

    # num of bytes received
    def get_recv(self):
        return self.recv
