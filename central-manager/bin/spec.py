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
