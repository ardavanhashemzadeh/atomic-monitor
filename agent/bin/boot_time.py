import psutil
import time


# convert to # hours, minutes, seconds
def sec_to_time(raw_sec):
    s = int(time.time()) - psutil.boot_time()

    minute = 60
    hour = minute * 60
    day = hour * 24

    d = s / day
    s -= d * day
    h = s / hour
    s -= h * hour
    m = s / minute
    s -= m * minute

    return d, h, m, s


class BootTime:
    # get system boot time
    def get_boot_time(self):
        status = psutil.boot_time()

        print(status)

        # day(s), hour(s), minute(s), second(s)
        return sec_to_time(status)
