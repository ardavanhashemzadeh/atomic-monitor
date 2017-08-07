class Server:
    def __init__(self, _id, _name, _typ, _mode, _host, _port):
        self.id = _id
        self.name = _name
        self.typ = _typ
        self.mode = _mode
        self.host = _host
        self.port = _port

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        return self.typ

    def get_mode(self):
        return self.mode

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port


class JSONServer:
    def __init__(self, _id, _name, _typ, _mode, _host, _port):
        self.id = _id
        self.name = _name
        self.typ = _typ
        self.mode = _mode
        self.host = _host
        self.port = _port

        self.online = False
        self.os = 'question'
        self.boottime = ''
        self.ping = -1
        self.cpu = -1
        self.ram = -1
        self.swap = -1
        self.load_onemin = -1
        self.load_fivemin = -1
        self.load_fifteenmin = -1
        self.disk_status = ''
        self.disk_percent = -1

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def set_specs(self, _online, _os, _boottime, _ping, _cpu, _ram, _swap, _load_1m, _load_5m, _load_15m, _disk_status,
                  _disk_percent):
        self.online = _online
        self.os = _os
        self.boottime = _boottime
        self.ping = _ping
        self.cpu = _cpu
        self.ram = _ram
        self.swap = _swap
        self.load_onemin = _load_1m
        self.load_fivemin = _load_5m
        self.load_fifteenmin = _load_15m
        self.disk_status = _disk_status
        self.disk_percent = _disk_percent


class Spec:
    def __init__(self, _hostname, _ip, _mac, _os, _cpu_brand, _cpu_speed, _ram, _uptime, _load_list):
        self.hostname = _hostname
        self.ip = _ip
        self.mac = _mac
        self.os = _os
        self.cpu_brand = _cpu_brand
        self.cpu_speed = _cpu_speed
        self.ram = _ram
        self.uptime = _uptime
        self.load_list = _load_list
        self.availability = -1

    def set_availability(self, _availability):
        self.availability = _availability


class Graph:
    def __init__(self, _id, _name, _typeserv, _mode):
        self.id = _id
        self.name = _name
        self.typeserv = _typeserv
        self.mode = _mode

        self.online = False
        self.timeline = []

        self.cpu_current = 0
        self.cpu_graph_max = 0
        self.cpu_graph_data = []

        self.ram_current = 0
        self.ram_graph_max = 0
        self.ram_graph_data = []

        self.swap_current = 0
        self.swap_graph_max = 0
        self.swap_graph_data = []

        self.load_current_1m = 0
        self.load_current_5m = 0
        self.load_current_15m = 0
        self.load_graph_max = 0
        self.load_graph_data_list = []

        self.ping_graph_max = 0
        self.ping_graph_data = []

        self.netdown_graph_max = 0
        self.netdown_graph_data = []

        self.netup_graph_max = 0
        self.netup_graph_data = []

        self.disk_device_list = []
        self.disk_data_list = []

    def set_online(self, _online):
        self.online = _online

    def set_timeline(self, _timeline):
        self.timeline = _timeline

    def set_graph_cpu(self, current, max_level, data):
        self.cpu_current = current
        self.cpu_graph_max = max_level
        self.cpu_graph_data = data

    def set_graph_ram(self, current, max_level, data):
        self.ram_current = current
        self.ram_graph_max = max_level
        self.ram_graph_data = data

    def set_graph_swap(self, current, max_level, data):
        self.swap_current = current
        self.swap_graph_max = max_level
        self.swap_graph_data = data

    def set_graph_load(self, current_1m, current_5m, current_15m, max_level, data_list):
        self.load_current_1m = current_1m
        self.load_current_5m = current_5m
        self.load_current_15m = current_15m
        self.load_graph_max = max_level
        self.load_graph_data_list = data_list

    def set_graph_ping(self, max_level, data):
        self.ping_graph_max = max_level
        self.ping_graph_data = data

    def set_graph_netdown(self, max_level, data):
        self.netdown_graph_max = max_level
        self.netdown_graph_data = data

    def set_graph_netup(self, max_level, data):
        self.netup_graph_max = max_level
        self.netup_graph_data = data

    def set_progbar_disks(self, device_list, data_list):
        self.disk_device_list = device_list
        self.disk_data_list = data_list


class Error:
    def __init__(self, _level, _name, _msg, _timestamp):
        self.level = _level
        self.name = _name
        self.msg = _msg
        self.timestamp = _timestamp


class NetData:
    def __init__(self, _name, _sent, _recv):
        self.name = _name
        self.sent = _sent
        self.recv = _recv

    def get_name(self):
        return self.name

    def get_sent(self):
        return self.sent

    def get_recv(self):
        return self.recv
