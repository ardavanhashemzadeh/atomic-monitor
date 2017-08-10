import platform
import os


class LoadAvg:
    # get system load average in 1 min, 5 min, & 15 min
    def get_load(self):
        if 'Windows' in platform.system():
            return False, None, None, None
        else:
            status = os.popen("uptime | awk -F'[a-z]:' '{ print $2}'").read().rstrip('\r\n').replace(' ', '').split(',')

            # 1 min, 5 min, 15 min load average
            return True, status[0], status[1], status[2]
