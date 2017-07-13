import psutil


def mb_convert(byts):
    return byts / 1024 / 1024


class Network:
    # get # of bytes sent & received
    def get_bytes_status(self):
        nics = list()

        # goes through the list of NICs (skipping lo/loopback)
        nic_list = psutil.net_io_counters(pernic=True)
        for net in nic_list.keys():
            # convert bytes to megabytes
            sent = mb_convert(nic_list[net].bytes_sent)
            recv = mb_convert(nic_list[net].bytes_recv)

            nics.append(NIC(net, sent, recv))

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
