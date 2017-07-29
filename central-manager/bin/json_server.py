class JSONServer:
    def __init__(self, _name, _typ, _mode, _host, _port):
        self.name = _name
        self.typ = _typ
        self.mode = _mode
        self.host = _host
        self.port = _port

        self.online = False
        self.boottime = ''
        self.ping = -1
        self.cpu = -1
        self.ram = -1
        self.swap = -1
        self.disk_status = ''
        self.disk_percent = -1

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port

    def set_specs(self, _online, _boottime, _ping, _cpu, _ram, _swap, _disk_status, _disk_percent):
        self.online = _online
        self.boottime = _boottime
        self.ping = _ping
        self.cpu = _cpu
        self.ram = _ram
        self.swap = _swap
        self.disk_status = _disk_status
        self.disk_percent = _disk_percent
