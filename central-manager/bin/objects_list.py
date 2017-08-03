class Disk:
    def __init__(self, _name, _percent, _used, _total):
        self.name = _name
        self.percent = _percent
        self.used = _used
        self.total = _total
    
    def get_name(self):
        return self.name

    def get_percent(self):
        return self.percent

    def get_used(self):
        return self.used

    def get_total(self):
        return self.total


class ErrorLog:
    def __init__(self, _servername, _timestamp, _type, _msg):
        self.servername = _servername
        self.timestamp = _timestamp
        self.typ = _type
        self.msg = _msg

    def get_servername(self):
        return self.servername

    def get_timestamp(self):
        # TODO
        return self.timestamp

    def get_type(self):
        return self.typ

    def get_msg(self):
        return self.msg
