# -*- coding: utf-8 -*-
from configparser import ConfigParser
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify

from urllib.request import urlopen
import pymysql
import pexpect
import json


# load config file
config = ConfigParser()
config.read('config.ini')
err_type = ''
log_file = ''
db_host = ''
db_port = 0
db_user = ''
db_pass = ''
db_name = ''
db_prefix = ''
interval_time = 0
flsk_host = ''
flsk_port = 0
try:
    # log values
    err_type = 'Log > URL'
    log_file = config.get('Log', 'URL')

    # database values
    err_type = 'Storage > Host'
    db_host = config.get('Storage', 'Host')
    err_type = 'Storage > Port'
    db_port = config.get('Storage', 'Port')
    err_type = 'Storage > User'
    db_user = config.get('Storage', 'User')
    err_type = 'Storage > Password'
    db_pass = config.get('Storage', 'Password')
    err_type = 'Storage > Database'
    db_name = config.get('Storage', 'Database')
    err_type = 'Storage > Prefix'
    db_prefix = config.get('Storage', 'Prefix')

    # collector
    interval_time = config.getint('Collector', 'Interval')

    # flask connection info
    flsk_host = config.get('UI_Feeder', 'Host')
    flsk_port = config.getint('UI_Feeder', 'Port')
except IOError:
    print('CONFIG ERROR: Unable to load values from \"{}\"!'.format(err_type))
    print('CONFIG ERROR: Force closing program...')
    exit()


# prepare log file
try:
    logger = open(config.get('Log', 'URL'))
except IOError:
    print('FILE ERROR: Unable to open file: {}!'.format(config.get('Log', 'URL')))
    print('FILE ERROR: Force closing program...')
    exit()


# setup flask
app = Flask(__name__)


# prepare database connection
con = None
cur = None


# log errors/debugging
def log(service, typ, msg):
    now = datetime.now()
    log_msg = '{} [{:^12}]: {}\r\n'.format(now.strftime('%m-%d-%Y %H:%M:%S'),
                                           service + ' ' + typ,
                                           msg)

    # print to console
    print(log_msg)
    try:
        logger.write(log_msg)
    except IOError as ex:
        print('FILE ERROR: Unable to write log to file! Reason: {}'.format(ex.args[0]))


# ping test server
def ping_server(host):
    # ping server
    result = pexpect.spawn('ping -c 1 {}'.format(host))

    try:
        # retrieve ping time
        p = result.readline()
        time_ping = float(p[p.find('time=') + 5:p.find(' ms')])

        # ping time
        return time_ping
    except ValueError:
        # ping time
        return -1


# insert new ping data to SQL database
def insert_log_data(server_name, typ, message):
    try:
        cur.execute('INSERT INTO {}_logs (server_name, type, msg) '
                    'VALUES (?, ?, ?)'.format(db_prefix), server_name, typ, message)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [error log] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_name, ex.args))


# insert new ping data to SQL database
def insert_ping_data(server_id, status, ping=None):
    try:
        cur.execute('INSERT INTO {}_ping_logs (server_id, status, ping) '
                    'VALUES (?, ?, ?)'.format(db_prefix), server_id, status, ping)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [memory] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_id, ex.args))


# insert new memory data to SQL database
def insert_memory_data(server_id, status, ram_percent=None, ram_used=None, ram_total=None, swap_percent=None,
                       swap_used=None, swap_total=None):
    try:
        cur.execute('INSERT INTO {}_memory_logs (server_id, status, ram_percent, ram_used, ram_total, swap_percent, '
                    'swap_used, swap_total) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'.format(db_prefix), server_id, status, ram_percent, ram_used,
                    ram_total, swap_percent, swap_used, swap_total)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [memory] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_id, ex.args))


# insert new CPU data to SQL database
def insert_cpu_data(server_id, status, cpu_percent=None):
    try:
        cur.execute('INSERT INTO {}_cpu_logs (server_id, status, cpu_percent) '
                    'VALUES (?, ?, ?)'.format(db_prefix), server_id, status, cpu_percent)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [cpu] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_id, ex.args))


# insert new network data to SQL database
def insert_net_data(server_id, status, name=None, sent=None, received=None):
    try:
        cur.execute('INSERT INTO {}_network_logs (server_id, status, name, sent, received) '
                    'VALUES (?, ?, ?, ?)'.format(db_prefix), server_id, status, name, sent, received)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [network] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_id, ex.args))


# insert new network data to SQL database
def insert_load_data(server_id, status, one_avg=None, five_avg=None, fifteen_avg=None):
    try:
        cur.execute('INSERT INTO {}_load_logs (server_id, status, 1m_avg, 5m_avg, 15m_avg) '
                    'VALUES (?, ?, ?, ?, ?)'.format(db_prefix), server_id, status, one_avg, five_avg, fifteen_avg)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [load] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_id, ex.args))


# insert new disk data to SQL database
def insert_disk_data(server_id, status, device=None, percent=None, used=None, total=None):
    try:
        cur.execute('INSERT INTO {}_disk_logs (server_id, status, device, percent, used, total) '
                    'VALUES (?, ?, ?, ?, ?, ?)'.format(db_prefix), server_id, status, device, percent, used, total)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [disk] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_id, ex.args))


# insert new disk I/O data to SQL database
def insert_disk_io_data(server_id, status, io=None):
    try:
        cur.execute('INSERT INTO {}_disk-io_logs (server_id, status, io) '
                    'VALUES (?, ?, ?)'.format(db_prefix), server_id, status, io)
        cur.commit()
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Unable to insert [disk] data for server [{}] to SQL database! STACKTRACE: {}'
            .format(server_id, ex.args))


# scrape data from each agent (server)
def scrape_data(time):
    while True:
        # retrieve list of servers
        servers = list()
        try:
            # get list of servers
            for row in cur.execute('SELECT * FROM {}_servers'.format(db_prefix)):
                servers.append(Server(row[0], row[1], row[2], row[3], row[4], row[5]))

            # go through each server and scrape data
            for serv in servers:
                ping_result = ping_server(serv.host)
                if ping_result is not -1:
                    try:
                        # sniff up data from a server
                        with urlopen('http://{}:{}/'.format(serv.host, serv.port)) as url:
                            data = json.loads(url.read().decode())

                            # insert data to SQL db
                            insert_ping_data(serv.id, 1, ping_result)
                            if ping_result > 200:
                                insert_log_data(serv.name, 0, 'Slow ping response: {} ms'.format(ping_result))

                            # insert ram data to SQL db
                            insert_memory_data(serv.id,
                                               1,
                                               data['memory']['ram']['percent_used'],
                                               data['memory']['ram']['used'],
                                               data['memory']['ram']['total'],
                                               data['memory']['swap']['percent_used'],
                                               data['memory']['swap']['used'],
                                               data['memory']['swap']['total'])
                            if data['memory']['ram']['percent_used'] >= 90:
                                insert_log_data(serv.name, 0, 'High RAM usage: {}%'.format(data['memory']['ram']
                                                                                           ['percent_used']))

                            # insert CPU data to SQL db
                            insert_cpu_data(serv.id,
                                            1,
                                            data['cpu']['percent_used'])
                            if data['cpu']['percent_used'] >= 90:
                                insert_log_data(serv.name, 0, 'High CPU usage: {}%'.format(data['cpu']['percent_used']))

                            # insert network data to SQL db
                            for net_nic in data['network']:
                                insert_net_data(serv.id,
                                                1,
                                                net_nic['name'],
                                                net_nic['mb_sent'],
                                                net_nic['mb_received'])

                            # insert load average data to SQL db
                            insert_load_data(serv.id,
                                             1,
                                             data['load']['1min'],
                                             data['load']['5min'],
                                             data['load']['15min'])
                            if data['load']['1min'] is not None:
                                if data['load']['1min'] > 1.00:
                                    insert_log_data(serv.name, 0,
                                                    'High 1m load usage: {}'.format(data['load']['1min']))
                                elif data['load']['5min'] > 1.00:
                                    insert_log_data(serv.name, 0,
                                                    'High 5m load usage: {}'.format(data['load']['5min']))
                                elif data['load']['15min'] > 1.00:
                                    insert_log_data(serv.name, 0,
                                                    'High 15m load usage: {}'.format(data['load']['15min']))

                            # insert disk data to SQL db
                            for disk in data['disks']['list']:
                                insert_disk_data(serv.id,
                                                 1,
                                                 disk['device'],
                                                 disk['percent_used'],
                                                 disk['used'],
                                                 disk['total'])
                                if disk['percent_used'] > 90:
                                    insert_log_data(serv.name, 0,
                                                    'High disk space usage: {}%'.format(disk['percent_used']))

                            log('CM', 'DEBUG', 'Retrieved and logged data for server [{}]!'.format(serv.name))
                    except pymysql.Error:
                        log('AGENT', 'ERROR', 'Unable to access server [{}]! Please make sure the port is open on that '
                                              'server!'.format(serv.name))
                else:
                    insert_ping_data(serv.id, 0)
                    insert_memory_data(serv.id, 0)
                    insert_cpu_data(serv.id, 0)
                    insert_net_data(serv.id, 0)
                    insert_load_data(serv.id, 0)
                    insert_disk_data(serv.id, 0)
                    insert_log_data(serv.name, 1, 'Server not responding to ping')
                    log('AGENT', 'WARN', 'Server [{}] is not responding, skipping...'.format(serv.name))
        except pymysql.Error as ex:
            log('SQL', 'ERROR', 'Problem when trying to retrieve data from the server! STACKTRACE: {}'.format(ex.args))
            log('SQL', 'ERROR', 'Force closing program...')
            exit()
        time.sleep(time)


# start Flask service: retrieve now status from a server
@app.route('/now/<hostname>/<port>')
def web_now_status(hostname, port):
    ping_result = ping_server(hostname)
    if ping_result is not -1:
        # access central-manager process
        with urlopen('http://{}:{}/now'.format(hostname, port)) as url:
            r = json.loads(url.read().decode())

            # get data
            ram_percent = r['ram']['percent_used']
            cpu_percent = r['cpu']['percent_used']
            boot_time = r['boot']['start_timestamp']
            disk_io = r['disk_io']

            # create json data
            json_data = {
                'status': 'online',
                'ping': ping_result,
                'ram_percent': ram_percent,
                'cpu_percent': cpu_percent,
                'boot_time': boot_time,
                'disk_io': disk_io
            }

            # print json data
            return jsonify(json_data)
    else:
        # create json data
        json_data = {
            'status': 'offline'
        }

        # print json data
        return jsonify(json_data)


# start Flask service: retrieve list of servers
@app.route('/servers')
def web_servers():
    servers = list()
    # access database to retrieve servers
    try:
        # retrieve data
        for row in cur.execute('SELECT * FROM {}_servers'.format(db_prefix)):
            servers.append(Server(row[0], row[1], row[2], row[3], row[4], row[5]))
        names = list()
        types = list()
        modes = list()
        hosts = list()
        ports = list()
        for server in servers:
            names.append(server.get_name())
            types.append(server.get_type())
            modes.append(server.get_mode())
            hosts.append(server.get_host())
            ports.append(server.get_ports())

        # create json data
        json_data = [
            {
                'name': name,
                'type': typ,
                'mode': mode,
                'host': host,
                'port': port
            }
            for name, typ, mode, host, port in zip(names, types, modes, hosts, ports)
        ]

        # print json data
        return jsonify(json_data)
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Error when trying to retrieve data from the database! STACKTRACE: {}'.format(ex.args))
        log('SQL', 'ERROR', 'Force closing program...')
        exit()


# start Flask service: retrieve latest errors
@app.route('/errors/<count>')
def web_errors(count):
    errors = list()
    # access database to retrieve errors
    try:
        # retrieve data
        for row in cur.execute('(SELECT * FROM {}_logs ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(db_prefix,
                                                                                                           count)):
            errors.append(ErrorLog(row[1], row[2], row[3], row[4]))
        servernames = list()
        timestamps = list()
        types = list()
        msgs = list()
        for error in errors:
            servernames.append(error.get_servername())
            timestamps.append(error.get_timestamp())
            types.append(error.get_type())
            msgs.append(error.get_msg())

        # create json data
        json_data = [
            {
                'server_name': server_name,
                'timestamp': timestamp,
                'type': typ,
                'msg': msg
            }
            for server_name, timestamp, typ, msg in zip(servernames, timestamps, types, msgs)
        ]

        # print json data
        return jsonify(json_data)
    except pymysql.Error as ex:
        log('SQL', 'ERROR', 'Error when trying to retrieve data from the database! STACKTRACE: {}'.format(ex.args))
        log('SQL', 'ERROR', 'Force closing program...')
        exit()


# main "method"
if __name__ == '__main__':
    # check to make sure the database has the required tables
    try:
        # connect to the database
        con = pymysql.connect(host=db_host,
                              port=db_port,
                              user=db_user,
                              passwd=db_pass,
                              db=db_name)
        cur = con.cursor()

        # create/check servers table
        # type:
        # GN : General server
        # DB : Database server
        # EM : Email Server
        # WB : Website Server
        # FW : Firewall System
        # AD : Active Directory Server
        # VM : Virtual Machine/Hypervisor Server
        # FS : File Sharing Server
        # SY : Security-Based Server
        # mode:
        # 0 : enabled
        # 1 : disabled
        # 2 : maintenance
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_servers (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    name VARCHAR(100) NOT NULL,
                    type CHAR(2) NOT NULL,
                    mode CHAR(1) NOT NULL,
                    hostname VARCHAR(255) NOT NULL,
                    port SMALLINT NOT NULL,
                    PRIMARY KEY(id));""".format(db_prefix))

        # create/check error logs table
        # type:
        # 0 : warning
        # 1 : error
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_logs (
                    id INTEGER NOT NULL AUTO_INCREMENT,
                    server_name VARCHAR(100) NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    type CHAR(1) NOT NULL,
                    msg VARCHAR(500) NOT NULL,
                    PRIMARY KEY(id));""")

        # create/check ping logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_ping_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    status ENUM(0,1),
                    ping DECIMAL(100,2),
                    PRIMARY KEY(id));""".format(db_prefix))

        # create/check memory logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_memory_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    status ENUM(0,1),
                    ram_percent DECIMAL(4,1),
                    ram_used DECIMAL(100,2),
                    ram_total DECIMAL(100,2),
                    swap_percent DECIMAL(4,1),
                    swap_used DECIMAL(100,2),
                    swap_total DECIMAL(100,2),
                    PRIMARY KEY(id));""".format(db_prefix))

        # create/check CPU logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_cpu_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    status ENUM(0,1),
                    cpu_percent DECIMAL(4,1),
                    PRIMARY KEY(id));""".format(db_prefix))

        # create/check network logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_network_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    status ENUM(0,1),
                    name VARCHAR(50),
                    sent BIGINT,
                    received BIGINT,
                    PRIMARY KEY(id));""".format(db_prefix))

        # create/check load logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_load_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    status ENUM(0,1),
                    1m_avg DECIMAL(5,1),
                    5m_avg DECIMAL(5,1),
                    15m_avg DECIMAL(5,1),
                    PRIMARY KEY(id));""".format(db_prefix))

        # create/check disk logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_disk_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    status ENUM(0,1),
                    device VARCHAR(50),
                    percent BIGINT,
                    used BIGINT,
                    total BIGINT,
                    PRIMARY KEY(id));""".format(db_prefix))

        # create/check disk logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_disk-io_logs (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    timestamp DATE DEFAULT GETDATE(),
                    status ENUM(0,1),
                    io DECIMAL(5,2),
                    PRIMARY KEY(id));""".format(db_prefix))

        # submit changes to SQL server
        cur.commit()
    except pymysql.Error as e:
        log('SQL', 'ERROR', 'Error when trying to check/create table! STACKTRACE: {}'.format(e.args))
        log('SQL', 'ERROR', 'Force closing program...')
        exit()

    # start scraping thread job!
    thd = Thread(target=scrape_data, args=(interval_time, ))
    thd.daemon = True
    thd.start()

    # start Flask service
    print('Starting CM service...')
    app.run(host=flsk_host, port=flsk_port)


class Server:
    def __init__(self, _id, _name, _type, _mode, _host, _port):
        self.id = _id
        self.name = _name
        self.typ = _type
        self.mode = _mode
        self.host = _host
        self.port = _port

    def get_id(self):
        return self.id

    def get_name(self):
        return self.name

    def get_type(self):
        return self.typ

    def get_mode(self):
        return self.mode

    def get_host(self):
        return self.host

    def get_port(self):
        return self.port


class ErrorLog:
    def __init__(self, _servername, _timestamp, _type, _msg):
        self.servername = _servername
        self.timestamp = _timestamp
        self.typ = _type
        self.msg = _msg

    def get_servername(self):
        return self.servername

    def get_timestamp(self):
        # TODO
        return self.timestamp

    def get_type(self):
        return self.typ

    def get_msg(self):
        return self.msg
