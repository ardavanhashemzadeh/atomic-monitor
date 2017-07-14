# -*- coding: utf-8 -*-
from configparser import ConfigParser
from flask import Flask, jsonify

from bin.ram import RAM
from bin.cpu import CPU
from bin.network import Network
from bin.load_avg import LoadAvg
from bin.boot_time import BootTime
from bin.disk import Disk
from bin.process import Process


# load config
config = ConfigParser()
config.read('config.ini')

# setup variables
sram = RAM()
scpu = CPU()
net = Network()
load = LoadAvg()
boot = BootTime()
sdisk = Disk()
proc = Process()
app = Flask(__name__)


# display full system specs
@app.route('/')
def web():
    # retrieve current system specs
    ram_percent, ram_used, ram_total = sram.get_memory_usage()
    swap_percent, swap_used, swap_total = sram.get_swap_usage()
    cpu_usage = scpu.get_usage()
    nics_bytes = net.get_bytes_status()
    nic_names, nic_sent, nic_recvs = [], [], []
    for nic in nics_bytes:
        nic_names.append(nic.get_name())
        nic_sent.append(nic.get_sent())
        nic_recvs.append(nic.get_recv())
    isLinux, load_1m, load_5m, load_15m = load.get_load()
    if not isLinux:
        load_1m = 'NULL'
        load_5m = 'NULL'
        load_15m = 'NULL'
    boot_time_days, boot_time_hr, boot_time_min, boot_time_sec = boot.get_boot_time()
    disks = sdisk.get_disks()
    disk_names, disk_percents, disk_uses, disk_totals = [], [], [], []
    for disk in disks:
        disk_names.append(disk.get_name())
        disk_percents.append(disk.get_percent())
        disk_uses.append(disk.get_used())
        disk_totals.append(disk.get_total())
    disk_io = sdisk.get_disk_io()
    processes = proc.get_processes()
    proc_ids, proc_names, proc_times, proc_statuses, proc_cpus, proc_rams = [], [], [], [], [], []
    for process in processes:
        proc_ids.append(process.get_id())
        proc_ids.append(process.get_name())
        proc_ids.append(process.get_time())
        proc_ids.append(process.get_status())
        proc_ids.append(process.get_cpu())
        proc_ids.append(process.get_ram())

    # create json object
    json_data = {
        'memory': {
            'ram': {
                'percent_used': ram_percent,
                'used': ram_used,
                'total': ram_total
            },
            'swap': {
                'percent_used': swap_percent,
                'used': swap_used,
                'total': swap_total
            }
        },
        'cpu': {
            'percent_used': cpu_usage
        },
        'network': [
            {
                'name': name,
                'mb_sent': sent,
                'mb_recieved': recv
            }
            for name, sent, recv in zip(nic_names, nic_sent, nic_recvs)
        ],
        'load': {
            '1min': load_1m,
            '5min': load_5m,
            '15min': load_15m
        },
        'boot': {
            'time': {
                'days': boot_time_days,
                'hours': boot_time_hr,
                'minutes': boot_time_min,
                'seconds': boot_time_sec
            }
        },
        'disks': {
            'io': disk_io,
            'list': [
                {
                    'name': name,
                    'percent_used': percent,
                    'used': used,
                    'total': total
                }
                for name, percent, used, total in zip(disk_names, disk_percents, disk_uses, disk_totals)
            ]
        },
        'process': [
            {
                'id': proc_id,
                'name': name,
                'time': time,
                'status': status,
                'cpu': cpu,
                'ram': ram
            }
            for proc_id, name, time, status, cpu, ram in zip(proc_ids, proc_names, proc_times, proc_statuses, proc_cpus, proc_rams)
        ]
    }

    # print json data
    return jsonify(json_data)


# start flask process
if __name__ == '__main__':
    print('Starting program...')
    app.run(host=config.get('System', 'Host'), port=config.getint('System', 'Port'))
