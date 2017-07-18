class Server:
    def __init__(self, _id, _name, _type, _mode, _host, _port):
        self.id = _id
        self.name = _name
        self.typ = _type
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
