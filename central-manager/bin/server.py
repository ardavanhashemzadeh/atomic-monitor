class Server:
	def __init__(self, _id, _name, _host, _port):
		self.id = _id
		self.name = _name
		self.host = _host
		self.port = _port
	
	def get_id(self):
		return self.id
	
	def get_name(self):
		return self.name
	
	def get_host(self):
		return self.host
	
	def get_port(self):
		return self.port
