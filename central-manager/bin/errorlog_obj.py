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
