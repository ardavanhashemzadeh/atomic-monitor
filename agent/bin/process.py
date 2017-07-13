import threading
import psutil


process_list = list()

# convert to # hours, minutes, seconds
def sec_to_time(raw_sec):
    minu, sec = divmod(raw_sec, 60)
    hr, minu = divmod(minu, 60)
    day, hr = divmod(hr, 24)

    return '{},{},{},{}'.format(day, hr, minu, sec)

# get process info in thread mode
def get_process_info(pid):
	proc = psutil.Process(pid)
	name = proc.name()
	time = sec_to_time(proc.create_time())
	status = proc.as_dict()['status']
	cpu = proc.cpu_percent(interval=1.0)
	ram = proc.memory_percent()
	process_list.append(ProcessID(pid, name, time, status, cpu, ram))


class Process:
    # get list of all current processes
    def get_processes(self):
	threads = list()
        process_list = list()
		# create new thread for each pid
		for pid in psutil.pids():
			thd = threading.Thread(target=NAME_HERE)
			thd.start()
			threads.append(thd)
		
		# force finish all threads to return result
		for thd in threads:
			thd.join()

        # list of processes w/ their specs
        return process_list


class ProcessID:
    def __init__(self, _id, _name, _time, _status, _cpu, _ram):
        self.id = _id
        self.name = _name
        self.time = _time
        self.status = _status
        self.cpu = _cpu
        self.ram = _ram

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_time(self):
        return self.time

    def get_status(self):
        return self.status

    def get_cpu(self):
        return self.cpu

    def get_ram(self):
        return self.ram
