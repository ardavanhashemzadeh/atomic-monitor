import psutil
import time


def mb_convert(byts):
    return byts / 1024 / 1024


class Network:
    # get # of bytes sent & received
    def get_bytes_status(self):
        nics = list()

        # get list of before sent/recv bytes from each NIC
        nic_names = list()
        before_list = list()
        nic_list = psutil.net_io_counters(pernic=True)
        for net in nic_list.keys():
            nic_names.append(net)
            before_list.append(NIC_IO(nic_list[net].bytes_sent, nic_list[net].bytes_recv))

        # wait between updates
        time.sleep(1)

        # get list of after sent/recv bytes from each NIC
        after_list = list()
        nic_list = psutil.net_io_counters(pernic=True)
        for net in nic_list.keys():
            after_list.append(NIC_IO(nic_list[net].bytes_sent, nic_list[net].bytes_recv))

        # do math to get difference in sent/recv
        for i in range(0, len(before_list) - 1):
            sent = mb_convert(after_list[i].sent - before_list[i].sent)
            recv = mb_convert(after_list[i].recv - before_list[i].recv)

            nics.append(NIC(nic_names[i], sent, recv))

        # NICs w/ num bytes sent/received
        return nics


class NIC_IO:
    def __init__(self, _sent, _recv):
        self.sent = _sent
        self.recv = _recv

    # num of bytes sent
    def get_sent(self):
        return self.sent

    # num of bytes received
    def get_recv(self):
        return self.recv


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
