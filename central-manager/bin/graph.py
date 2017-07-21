class Graph:
    def __init__(self, _name, _typeserv, _mode):
        self.name = _name
        self.typeserv = _typeserv
        self.mode = _mode
    
    def set_online(self, _online):
        self.online = _online
    
    def set_graph_cpu(self, current, max_level, timeline, data):
        self.cpu_current = current
        self.cpu_graph_max = max_level
        self.cpu_graph_timeline = timeline
        self.cpu_graph_data = data
    
    def set_graph_ram(self, current, max_level, timeline, data):
        self.ram_current = current
        self.ram_graph_max = max_level
        self.ram_graph_timeline = timeline
        self.ram_graph_data = data
    
    def set_graph_swap(self, current, max_level, timeline, data):
        self.swap_current = current
        self.swap_graph_max = max_level
        self.swap_graph_timeline = timeline
        self.swap_graph_data = data
    
    def set_graph_load(self, max_level, timeline, data_list):
        self.load_graph_max = max_level
        self.load_graph_timeline = timeline
        self.load_graph_data_list = data_list
    
    def set_graph_ping(self, max_level, timeline, data):
        self.ping_graph_max = max_level
        self.ping_graph_timeline = timeline
        self.ping_graph_data = data
    
    def set_graph_netdown(self, max_level, timeline, data):
        self.netdown_graph_max = max_level
        self.netdown_graph_timeline = timeline
        self.netdown_graph_data = data
    
    def set_graph_netup(self, max_level, timeline, data):
        self.netup_graph_max = max_level
        self.netup_graph_timeline = timeline
        self.netup_graph_data = data

    def set_progbar_disks(self, device_list, data_list):
        self.disk_device_list = device_list
        self.disk_data_list = data_list
