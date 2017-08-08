import psutil


def gb_convert(byts):
    return byts / 1024 / 1024 / 1024


class Memory:
    # get RAM usage
    def get_memory_usage(self):
        status = psutil.virtual_memory()

        used = gb_convert(status.used)
        total = gb_convert(status.total)

        # percentage, used & total in gb
        return round(status.percent, 0), round(used, 2), round(total, 2)

    # get swap usage
    def get_swap_usage(self):
        status = psutil.swap_memory()

        used = gb_convert(status.used)
        total = gb_convert(status.total)

        # percentage, used & total in gigabyte(s)
        return round(status.percent, 0), round(used, 2), round(total, 2)
