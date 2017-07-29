# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from configparser import ConfigParser
from uuid import getnode as get_mac
from datetime import datetime
from threading import Thread
import platform
import cpuinfo
import psutil
import socket
import time

from bin.boot_time import BootTime
from bin.load_avg import LoadAvg
from bin.network import Network
from bin.disk import Disk
from bin.ram import RAM
from bin.cpu import CPU


# version
VERSION = '1.0'

# global attributes
ram_percent = 0
ram_used = 0
ram_total = 0
swap_percent = 0
swap_used = 0
swap_total = 0
cpu_percent = 0
boot_time = ''
network_list = []
disk_list = []
load_1min = ''
load_5min = ''
load_15min = ''


# convert human sizes to bytes
def convert_bytes(byts):
    try:
        byts = byts.lower()
        if byts.endswith('kb'):
            return int(byts[0:-2]) * 1024
        elif byts.endswith('mb'):
            return int(byts[0:-2]) * 1024 * 1024
        elif byts.endswith('gb'):
            return int(byts[0:-2]) * 1024 * 1024 * 1024
        
        # for anything else... just throw an exception, we care zero
        raise IOError('Invalid input. Correct format: #kb/#mb/#gb like 10gb or 5mb')
        
    except Exception as error:
        raise Exception('Invalid input. Correct format: #kb/#mb/#gb like 10gb or 5mb. An error ' +
                        repr(error) + ' occurred.')


# load config
config = ConfigParser()
config.read('config.ini')
err_type = ''
log_file = ''
flsk_host = ''
flsk_port = 0
try:
    # log values
    err_type = 'Log > Name'
    log_file = config.get('Log', 'Name', fallback='agent.log')

    # flask values
    err_type = 'Flask > Host'
    flsk_host = config.get('Flask', 'Host', fallback='0.0.0.0')
    err_type = 'Flask > Port'
    flsk_port = config.getint('Flask', 'Port', fallback=5000)
except IOError as e:
    print('CONFIG ERROR: Unable to load values from \"{}\"! STACKTRACE: {}'.format(err_type, e.args[1]))
    print('CONFIG ERROR: Force closing program...')
    exit()


# prepare logging
logger = None
try:
    logger = open(log_file, 'a')
except IOError as e:
    print('FILE ERROR: Unable to open log file! STACETRACE: {}'.format(e.args[1]))
    print('FILE ERROR: Force closing program...')
    exit()


# perform logging
LOG_FORMAT = '{} | {:6s} | {:6s} | {}'


def log(level, typ, message):
    try:
        print(LOG_FORMAT.format(datetime.now().strftime('%Y-%m-%d %X'),
                                level,
                                typ,
                                message))
        logger.write(LOG_FORMAT.format(datetime.now().strftime('%Y-%m-%d %X'),
                                       level,
                                       typ,
                                       message) + '\n')
        logger.flush()
    except IOError as ex:
        print(LOG_FORMAT.format(datetime.now().strftime('%Y-%m-%d %X'),
                                'ERROR',
                                'AGENT',
                                'Unable to log to file! STACKTRACE: {}'.format(ex.args[1])))


# setup variables
sram = RAM()
scpu = CPU()
net = Network()
load = LoadAvg()
boot = BootTime()
sdisk = Disk()
app = Flask(__name__)


# display system hardware specs
@app.route('/specs')
def web_specs():
    # retrieve current system hardware specs
    operating_system = platform.platform()
    cpu_brand = cpuinfo.get_cpu_info()['brand']
    cpu_cores = '{} cores @ {}'.format(cpuinfo.get_cpu_info()['count'],
                                       cpuinfo.get_cpu_info()['hz_advertised'])
    total_ram = '{} GB'.format(round(psutil.virtual_memory().total / 1024 / 1024 / 1024), 0)
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))
    is_linux, load_1m, load_5m, load_15m = load.get_load()
    if not is_linux:
        load_1m = 'NULL'
        load_5m = 'NULL'
        load_15m = 'NULL'

    # create json data
    json_data = {
        'version': VERSION,
        'hostname': socket.gethostname(),
        'ip': s.getsockname()[0],
        'mac': ':'.join(("%012X" % get_mac())[i:i+2] for i in range(0, 12, 2)),
        'os': operating_system,
        'cpu_brand': cpu_brand,
        'cpu_cores': cpu_cores,
        'ram': total_ram,
        'boot': boot_time,
        'load': {
            '1min': load_1m,
            '5min': load_5m,
            '15min': load_15m
        }
    }

    log('INFO', 'AGENT', 'Retrieved hardware specs for IP: {}'.format(request.remote_addr))

    # print json data
    return jsonify(json_data)


# display current specs
@app.route('/now')
def web_now():
    # create json object
    json_data = {
        'version': VERSION,
        'ram': {
            'percent': ram_percent,
            'used': ram_used,
            'total': ram_total,
        },
        'swap': {
            'percent': swap_percent,
            'used': swap_used,
            'total': swap_total
        },
        'cpu': {
            'percent': cpu_percent
        },
        'boot': {
            'timestamp': boot_time
        },
        'disks': []
    }
    for disk in disk_list:
        json_data['disks'].append(disk.__dict__)

    log('INFO', 'AGENT', 'Retrieved now status for IP: {}'.format(request.remote_addr))

    # print json data
    return jsonify(json_data)


# display full system specs
@app.route('/all')
def web_all():
    # create json object
    json_data = {
        'version': VERSION,
        'memory': {
            'ram': {
                'percent': ram_percent,
                'used': ram_used,
                'total': ram_total,

            },
            'swap': {
                'percent': swap_percent,
                'used': swap_used,
                'total': swap_total
            }
        },
        'cpu': {
            'percent': cpu_percent
        },
        'network': [],
        'load': {
            '1min': load_1min,
            '5min': load_5min,
            '15min': load_15min
        }
    }
    for nic in network_list:
        json_data['network'].append(nic.__dict__)

    log('INFO', 'AGENT', 'Retrieved all status for IP: {}'.format(request.remote_addr))

    # print json data
    return jsonify(json_data)


# auto update values
def specs_updater():
    global ram_percent, ram_used, ram_total, swap_percent, swap_used, swap_total, cpu_percent, boot_time, network_list, \
        disk_list, load_1min, load_5min, load_15min

    while True:
        # update RAM info
        ram_percent, ram_used, ram_total = sram.get_memory_usage()

        # update swap info
        swap_percent, swap_used, swap_total = sram.get_swap_usage()

        # update cpu info
        cpu_percent = scpu.get_usage()

        # update boot time
        boot_time = boot.get_boot_time()

        # update network info
        network_list = net.get_nic_status()

        # update disk info
        disk_list = sdisk.get_disks()

        is_linux, load_1min, load_5min, load_15min = load.get_load()
        if not is_linux:
            load_1min = 'NULL'
            load_5min = 'NULL'
            load_15min = 'NULL'
        time.sleep(1)


# start flask process
if __name__ == '__main__':
    log('INFO', 'AGENT', 'Starting program...')

    log('INFO', 'AGENT', 'Starting auto updater...')
    thd = Thread(target=specs_updater)
    thd.daemon = True
    thd.start()
    log('INFO', 'AGENT', 'Auto updater started!')

    # wait 2 seconds so the updater can go through its first job
    time.sleep(2)

    # start Flask service
    log('INFO', 'AGENT', 'Now listening for HTTP requests...')
    app.run(host=flsk_host, port=flsk_port, threaded=True)
