class Server:
    def __init__(self, _name, _typeserv, _mode):
        self.name = _name
        self.typeserv = _typeserv
        self.mode = _mode
    
    def set_online(self, _online):
        self.online = _online

    def set_boottime(self, _boottime):
        self.boottime = _boottime
    
    def set_ping(self, _ping):
        self.ping = _ping

    def set_cpu(self, _cpu):
        self.cpu = _cpu
    
    def set_ram(self, _ram):
        self.ram = _ram
    
    def set_swap(self, _swap):
        self.swap = _swap
    
    def set_disk_status(self, _status):
        self.status = _status
    
    def set_disk_percent(self, _disk):
        self.disk = _disk
