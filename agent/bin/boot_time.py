from uptime import boottime


class BootTime:
    # get system boot time
    def get_boot_time(self):
        # datetime of boot
        return boottime().strftime('%x %X')
