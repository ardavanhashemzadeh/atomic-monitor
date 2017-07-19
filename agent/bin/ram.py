import psutil


def gb_convert(byts):
    return byts / 1024 / 1024 / 1024


class RAM:
    # get RAM usage
    def get_memory_usage(self):
        status = psutil.virtual_memory()

        used = gb_convert(status.used)
        active = gb_convert(status.active)
        inactive = gb_convert(status.inactive)
        buffers = gb_convert(status.buffers)
        cached = gb_convert(status.cached)
        shared = gb_convert(status.shared)
        total = gb_convert(status.total)

        # percentage, used, active, inactive, buffers, cached, shared, and total in gb
        return status.percent, used, active, inactive, buffers, cached, shared, total

    # get swap usage
    def get_swap_usage(self):
        status = psutil.swap_memory()

        used = gb_convert(status.used)
        total = gb_convert(status.total)

        # percentage, used & total in gigabyte(s)
        return status.percent, used, total
