from threading import Thread
import psutil
import time


nics = list()


# convert bytes to megabytes
def bytes_to_mb(byts):
    return byts / 1024 / 1024


# loop every second to update records
def update_nics():
    global nics
    while True:
        old_nics = nics
        new_nics = list()

        # get current status
        nic_list = psutil.net_io_counters(pernic=True)
        for net in nic_list.keys():
            new_nics.append(NIC(net, nic_list[net].bytes_sent, nic_list[net].bytes_recv))

        # do math to get change in 1 second difference
        nics = list()
        for i in range(0, len(old_nics)):
            diff_sent = bytes_to_mb(old_nics[i].get_sent() - new_nics[i].get_sent())
            diff_recv = bytes_to_mb(old_nics[i].get_recv() - new_nics[i].get_recv())

            nics.append(NIC(old_nics[i].get_name(),
                            diff_sent,
                            diff_recv))

        time.sleep(1)


class Network:
    def __init__(self):
        global nics
        # initial list
        nic_list = psutil.net_io_counters(pernic=True)
        for net in nic_list.keys():
            nics.append(NIC(net, nic_list[net].bytes_sent, nic_list[net].bytes_recv))

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
