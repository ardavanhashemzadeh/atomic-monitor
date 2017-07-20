import psutil


class CPU:
    # get CPU usage
    def get_usage(self):
        status = psutil.cpu_times_percent(interval=1, percpu=False)

        # total - idle = cpu load percentage
        return round(100.0 - status.idle, 1)
