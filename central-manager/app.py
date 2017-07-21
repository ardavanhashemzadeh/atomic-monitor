# -*- coding: utf-8 -*-
from flask import Flask, jsonify, request
from configparser import ConfigParser
from warnings import filterwarnings
from urllib.request import urlopen
from threading import Thread
import pymysql
import pexpect
import json

import bin.db_management as db_management
from bin.server import Server
from bin.error import Error
from bin.graph import Graph
from bin.spec import Spec


# convert human sizes to bytes
def convert_bytes(byts):
    try:
        if byts.endswith('kb'):
            return byts[0:-2] * 1024
        elif byts.endswith('mb'):
            return byts[0:-2] * 1024 * 1024
        elif byts.endswith('gb'):
            return byts[0:-2] * 1024 * 1024 * 1024
        else:
            raise IOError('Invalid input. Correct format: #kb/#mb/#gb like 10gb or 5mb')
    except ValueError:
        raise IOError('Invalid input. Correct format: #kb/#mb/#gb like 10gb or 5mb')


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
    err_type = 'Log > Name'
    log_file = config.get('Log', 'Name', fallback='agent.log')

    # database values
    err_type = 'Storage > Host'
    db_host = config.get('Storage', 'Host', fallback='localhost')
    err_type = 'Storage > Port'
    db_port = config.getint('Storage', 'Port', fallback=3306)
    err_type = 'Storage > User'
    db_user = config.get('Storage', 'User', fallback='root')
    err_type = 'Storage > Password'
    db_pass = config.get('Storage', 'Pass', fallback='password')
    err_type = 'Storage > Database'
    db_name = config.get('Storage', 'Database', fallback='agent')
    err_type = 'Storage > Prefix'
    db_prefix = config.get('Storage', 'Prefix', fallback='am')

    # collector
    err_type = 'Collector > Interval'
    interval_time = config.getint('Collector', 'Interval', fallback=1)

    # flask connection info
    err_type = 'UI_Feeder > Host'
    flsk_host = config.get('UI_Feeder', 'Host', fallback='0.0.0.0')
    err_type = 'UI_Feeder > Port'
    flsk_port = config.getint('UI_Feeder', 'Port', fallback=5001)
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


# setup flask
app = Flask(__name__)


# prepare database connection
con = None
cur = None
filterwarnings('ignore', category=pymysql.Warning)


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


# scrape data from each agent (server)
def scrape_data(time):
    while True:
        # retrieve list of servers
        servers = list()
        try:
            # get list of servers
            for row in cur.execute('SELECT * FROM {}_server'.format(db_prefix)):
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
                            db_management.insert_ping_data(logging, cur, db_prefix, con, serv.name, serv.id, 1, ping_result)
                            if ping_result > 200:
                                db_management.insert_log_data(logging, con, cur, serv.name, 0,
                                                              'Slow ping response: {} ms'.format(ping_result))

                            # insert ram data to SQL db
                            db_management.insert_memory_data(logging, cur, db_prefix, con, serv.name, serv.id, 1,
                                                             data['memory']['ram']['percent'],
                                                             data['memory']['ram']['used'],
                                                             data['memory']['ram']['active'],
                                                             data['memory']['ram']['inactive'],
                                                             data['memory']['ram']['buffers'],
                                                             data['memory']['ram']['cached'],
                                                             data['memory']['ram']['shared'],
                                                             data['memory']['ram']['total'],
                                                             data['memory']['swap']['percent'],
                                                             data['memory']['swap']['used'],
                                                             data['memory']['swap']['total'])
                            
                            # log if RAM/swap is 90% or above
                            if data['memory']['ram']['percent'] >= 90:
                                db_management.insert_log_data(logging, con, cur, serv.name, 0,
                                                              'High RAM usage: {}%'.format(
                                                                  data['memory']['ram']['percent']))
                            if data['memory']['swap']['percent'] >= 90:
                                db_management.insert_log_data(logging, con, cur, serv.name, 0,
                                                              'High swap usage: {}%'.format(
                                                                  data['memory']['swap']['percent']))

                            # insert CPU data to SQL db
                            db_management.insert_cpu_data(logging, cur, db_prefix, con, serv.name, serv.id, 1, 
                                                          data['cpu']['percent'])

                            # log if CPU is 90% or above
                            if data['cpu']['percent'] >= 90:
                                db_management.insert_log_data(logging, con, cur, serv.name, 0,
                                                              'High CPU usage: {}%'.format(data['cpu']['percent']))

                            # insert network data to SQL db
                            for net_nic in data['network']:
                                db_management.insert_net_data(logging, cur, db_prefix, con, serv.name, serv.id, 1, 
                                                              net_nic['name'],
                                                              net_nic['sent'], 
                                                              net_nic['received'])

                            # insert load average data to SQL db
                            db_management.insert_load_data(logging, cur, db_prefix, con, serv.name, serv.id, 1, 
                                                           data['load']['1min'],
                                                           data['load']['5min'], 
                                                           data['load']['15min'])
                            
                            # log if load average is 1.00 or above
                            if data['load']['1min'] is not None:
                                if data['load']['1min'] > 1.00:
                                    db_management.insert_log_data(logging, con, cur, serv.name, 0,
                                                                  'High 1m load usage: {}'.format(data['load']['1min']))
                                elif data['load']['5min'] > 1.00:
                                    db_management.insert_log_data(logging, con, cur, serv.name, 0,
                                                                  'High 5m load usage: {}'.format(data['load']['5min']))
                                elif data['load']['15min'] > 1.00:
                                    db_management.insert_log_data(logging, con, cur, serv.name, 0,
                                                                  'High 15m load usage: {}'.format(
                                                                      data['load']['15min']))

                            log('INFO', 'CM', 'Retrieved and logged data for server [{}]!'.format(serv.name))
                    
                    except pymysql.Error:
                        log('ERROR', 'CM', 'Unable to access server [{}]! Please make sure the port is open on that server!'.format(serv.name))
                else:
                    db_management.insert_ping_data(logging, cur, db_prefix, con, serv.name, serv.id, 0)
                    db_management.insert_memory_data(logging, cur, db_prefix, con, serv.name, serv.id, 0)
                    db_management.insert_cpu_data(logging, cur, db_prefix, con, serv.name, serv.id, 0)
                    db_management.insert_net_data(logging, cur, db_prefix, con, serv.name, serv.id, 0)
                    db_management.insert_load_data(logging, cur, db_prefix, con, serv.name, serv.id, 0)
                    db_management.insert_disk_io_data(logging, cur, db_prefix, con, serv.name, serv.id, 0)
                    db_management.insert_log_data(logging, cur, db_prefix, con, serv.name, 1, 'Server not responding to ping')
                    log('WARN', 'CM', 'Server [{}] is not responding, skipping...'.format(serv.name))
        except pymysql.Error as ex:
            log('ERROR', 'CM', 'Problem when trying to retrieve data from SQL database! STACKTRACE: {}'.format(ex.args[1]))
            log('ERROR', 'CM', 'Force closing program...')
            exit()
        time.sleep(time)


# retrieve now status for index.html page
@app.route('/home')
def web_home():
    # retrieve list of servers
    servers = list()
    try:
        for row in cur.execute('SELECT * FROM {}_server'.format(db_prefix)):
            server = Server(row[0], row[1], row[2])
            hostname = row[3]
            port = row[4]
            
            # check if server is online & responding
            ping_result = ping_server(hostname)
            if ping_result is not -1:

                # retrieve now status from the agent
                with urlopen('http://{}:{}/now'.format(hostname, port)) as url:
                    r = json.loads(url.read().decode())
                    cpu_percent = r['cpu']['percent']
                    ram_percent = r['ram']['percent']
                    swap_percent = r['swap']['percent']
                    boot_timestamp = r['boot']['timestamp']
                    disk_status = ''
                    disk_percent = 0
                    for disk in r['disks']:
                        if disk['percent'] >= 70 and disk['percent'] < 90:
                            disk_status += "Device '{}' at {}% full".format(disk['name'], disk['percent'])
                            disk_percent = disk['percent']
                            break
                        elif disk['percent'] >= 90:
                            disk_status += "Device '{}' at {}% full".format(disk['name'], disk['percent'])
                            disk_percent = disk['percent']
                            break
                    
                    # assign them to HomeServer object
                    server.set_online(True)
                    server.set_boottime(boot_timestamp)
                    server.set_ping(ping_result)
                    server.set_cpu(cpu_percent)
                    server.set_ram(ram_percent)
                    server.set_swap(swap_percent)
                    server.set_disk_status(disk_status)
                    server.set_disk_percent(disk_percent)

                    # add to the list
                    servers.append(server)

            else:
                # assign empty values to HomeServer object
                server.set_online(True)
                server.set_boottime(0)
                server.set_ping(0)
                server.set_cpu(0)
                server.set_ram(0)
                server.set_swap(0)
                server.set_disk_status('Server not responding')
                server.set_disk_percent(-1)
                
                # add to the list   
                servers.append(server)
        
        # convert HomeServer list object into json_data
        json_data = {
            'status': 'good',
            'data': []
        }
        json_data = json.dumps(json_data)
        for server in servers:
            json_data['data'].append(server.__dict__)

        # print json data
        return jsonify(json_data)

    except pymysql.Error as sql_err:
        log('ERROR', 'CM', 'Unable to retrieve list of servers from SQL database! STACKTRACE: {}'.format(sql_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #home_sql', 'message': 'Unable to retrieve list of servers from SQL database! Please check logs.' }
        return jsonify(json_data)

    except Exception as plain_err:
        log('ERROR', 'CM', 'Unable to process through list of servers! STACKTRACE: {}'.format(plain_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #home_plain', 'message': 'Unable to process through list of servers! Please check logs.' }
        return jsonify(json_data)


@app.route('/server_names')
def web_server_names():
    # retrieve list of server names
    try:
        server_names = []
        for row in cur.execute('SELECT name FROM {}_server'.format(db_prefix)):
            server_names.append(row[0])
        
        # convert to json data
        json_data = server_names.__dict__

        # print json data
        return jsonify(json_data)


@app.route('/graph/<name>/<seconds_timeline>')
def web_graph(name, seconds_timeline):
    # retrieve hostname & port for server
    try:
        typeserv = ''
        mode = ''
        hostname = ''
        port = 0
        row = cur.execute('SELECT type, mode, hostname, port FROM {}_server WHERE name=%s'.format(db_prefix), name).fetchone()
        typeserv = row[0]
        mode = row[1]
        hostname = row[2]
        port = row[3]

        # create graph object
        server_graph = Graph(name, typeserv, mode)

        # check if server is online & responding
        ping_result = ping_server(hostname)
        if ping_result is not -1:
            server_graph.is_online(True)
        else:
            server_graph.is_online(False)

        # retrieve CPU graph data
        cpu_current = 0
        with urlopen('http://{}:{}/now'.format(hostname, port)) as url:
            r = json.loads(url.read().decode())
            cpu_current = r['cpu']['percent']
        # TODO get list of CPU percentage data based on timeline
        cpu_timeline = []
        cpu_data = []
        server_graph.set_graph_cpu(cpu_current, 100, cpu_timeline, cpu_data)

        # retrieve RAM graph data
        ram_current = 0
        ram_max = 0
        with urlopen('http://{}:{}/now'.format(hostname, port)) as url:
            r = json.loads(url.read().decode())
            ram_current = r['ram']['percent']
            ram_max = r['ram']['total']
        # TODO get list of RAM percentage data based on timeline
        ram_timeline = []
        ram_data = []
        server_graph.set_graph_ram(ram_current, ram_max, ram_timeline, ram_data)

        # retrieve swap graph data
        swap_current = 0
        swap_max = 0
        with urlopen('http://{}:{}/now'.format(hostname, port)) as url:
            r = json.loads(url.read().decode())
            swap_current = r['swap']['percent']
            swap_max = r['swap']['total']
        # TODO get list of swap percentage data based on timeline
        swap_timeline = []
        swap_data = []
        server_graph.set_graph_swap(swap_current, swap_max, swap_timeline, swap_data)

        # retrieve load graph data
        # TODO get list of load percentage data based on timeline
        load_timeline = []
        load_data_list = []
        server_graph.set_graph_load(1.5, load_timeline, load_data_list)

        # retrieve network download graph data
        # TODO get list of network download data based on timeline
        netdown_timeline = []
        netdown_max = []
        netdown_data = []
        server_graph.set_graph_netdown(netdown_max, netdown_timeline, netdown_data)

        # retrieve network upload graph data
        # TODO get list of network upload data based on timeline
        netup_timeline = []
        netup_max = []
        netup_data = []
        server_graph.set_graph_netup(netup_max, netup_timeline, netup_data)

        # retrieve disk progressbar data
        disk_device_list = []
        disk_data_list = []
        with urlopen('http://{}:{}/now'.format(hostname, port)) as url:
            r = json.loads(url.read().decode())
            for disk in r['disks']:
                disk_device_list.append(disk['name'])
                disk_data_list.append(disk['percent'])
        server_graph.set_progbar_disks(self, disk_device_list, disk_data_list)

        # convert HomeServer list object into json_data
        json_data = { 'status': 'good', 'data': server_graph.__dict__ }

        # print json data
        return jsonify(json_data)

    except pymysql.Error as sql_err:
        log('ERROR', 'CM', 'Unable to retrieve info for server [{}] from SQL database! STACKTRACE: {}'.format(name, sql_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #graph_sql', 'message': 'Unable to retrieve info for server [{}] from SQL database! Please check logs.'.format(name) }
        return jsonify(json_data)

    except Exception as plain_err:
        log('ERROR', 'CM', 'Unable to process graph info for server [{}]! STACKTRACE: {}'.format(name, plain_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #graph_plain', 'message': 'Unable to process graph info for server [{}]! Please check logs.'.format(name) }
        return jsonify(json_data)


@app.route('/specs/<name>')
def web_specs(name):
    # retrieve hostname & port for server
    try:
        hostname = ''
        port = 0
        row = cur.execute('SELECT hostname, port FROM {}_server WHERE name=%s'.format(db_prefix), name).fetchone()
        hostname = row[0]
        port = row[1]

        # check if server is online & responding
        ping_result = ping_server(hostname)
        if ping_result is -1:
            # create json data
            json_data = { 'status': 'error #specs_offline', 'message': 'Unable to retrieve hardware specifications for server [{}] because the server is not responding to ping! '
                                                                       'Either it\'s broken or offline.'.format(name) }
            
            # let webpanel know that the agent server can't be reached
            return jsonify(json_data)
        else:
            # retrieve hardware specifications
            specs = None
            with urlopen('http://{}:{}/specs'.format(hostname, port)) as url:
                r = json.loads(url.read().decode())
                specs = Spec(r['hostname'], 
                             r['ip'],
                             r['mac'],
                             r['os'],
                             r['cpu_brand'],
                             r['cpu_cores'],
                             r['ram'],
                             r['boot'],
                             [ r['load']['1min'], r['load']['5min'],r['load']['15min'] ])

            # calculate server's availability
            row = cur.execute('''SELECT FLOOR((alive.num / total.num) * 100
                              FROM (
                                  SELECT COUNT(status) as num FROM ping WHERE status != 1
                              ) alive
                              JOIN (
                                  SELECT COUNT(status) as num FROM ping
                              ) total;''').fetchone()
            specs.set_availability(row[0])

            # convert to json data
            json_data = { 'status': 'good', 'data': specs.__dict__ }

            # print json data
            return jsonify(json_data)

    except pymysql.Error as sql_err:
        log('ERROR', 'CM', 'Unable to retrieve info for server [{}] from SQL database! STACKTRACE: {}'.format(name, sql_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #graph_sql', 'message': 'Unable to retrieve info for server [{}] from SQL database! Please check logs.'.format(name) }
        return jsonify(json_data)

    except Exception as plain_err:
        log('ERROR', 'CM', 'Unable to process graph info for server [{}]! STACKTRACE: {}'.format(name, plain_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #graph_plain', 'message': 'Unable to process graph info for server [{}]! Please check logs.'.format(name) }
        return jsonify(json_data)


@app.route('/server_logs/<name>/<level>/<count>/<search_for>/<filter_out>')
def web_server_logs(name, level, count, search_for, filter_out):
    errors = list()
    # retrieve errors
    try:
        rows = None
        if level is -1:
            rows = cur.execute('(SELECT * FROM {}_log WHERE server_name=%s AND msg LIKE %s AND msg NOT LIKE %s ORDER BY id DESC LIMIT %d) ORDER BY id DESC'.format(db_prefix, 
                               name,
                               '%{}%'.format(search_for),
                               '%{}%'.format(filter_out),
                               count)
        else:
            rows = cur.execute('(SELECT * FROM {}_log WHERE server_name=%s AND type=%d msg LIKE %s AND msg NOT LIKE %s ORDER BY id DESC LIMIT %d) ORDER BY id DESC'.format(db_prefix),
                               name,
                               level,
                               '%{}%'.format(search_for),
                               '%{}%'.format(filter_out),
                               count)
        for row in rows:
            errors.append(Error(row[3], row[1], row[4], row[2]))
        
        # convert to json
        json_data = {
            'status': 'good',
            'data': []
        }
        json_data = json.dumps(json_data)
        for error in errors:
            json_data['data'].append(error.__dict__)

        # print json data
        return jsonify(json_data)

    except pymysql.Error as sql_err:
        log('ERROR', 'CM', 'Unable to retrieve error logs for server [{}] from SQL database! STACKTRACE: {}'.format(name, sql_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #server_error_logs_sql', 'message': 'Unable to retrieve error logs for server [{}] from SQL database! Please check logs.'.format(name) }
        return jsonify(json_data)

    except Exception as plain_err:
        log('ERROR', 'CM', 'Unable to process error logs for server [{}]! STACKTRACE: {}'.format(name, plain_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #server_error_logs_plain', 'message': 'Unable to process error logs for server [{}]! Please check logs.'.format(name) }
        return jsonify(json_data)


@app.route('/all_logs/<level>/<count>/<search_for>/<filter_out>')
def web_all_logs(level, count, search_for, filter_out):
    errors = list()
    # retrieve errors
    try:
        rows = None
        if level is -1:
            rows = cur.execute('(SELECT * FROM {}_log WHERE msg LIKE %s AND msg NOT LIKE %s ORDER BY id DESC LIMIT %d) ORDER BY id DESC'.format(db_prefix, 
                               '%{}%'.format(search_for),
                               '%{}%'.format(filter_out),
                               count)
        else:
            rows = cur.execute('(SELECT * FROM {}_log WHERE type=%d msg LIKE %s AND msg NOT LIKE %s ORDER BY id DESC LIMIT %d) ORDER BY id DESC'.format(db_prefix),
                               level,
                               '%{}%'.format(search_for),
                               '%{}%'.format(filter_out),
                               count)
        for row in rows:
            errors.append(Error(row[3], row[1], row[4], row[2]))
        
        # convert to json
        json_data = {
            'status': 'good',
            'data': []
        }
        json_data = json.dumps(json_data)
        for error in errors:
            json_data['data'].append(error.__dict__)

        # print json data
        return jsonify(json_data)

    except pymysql.Error as sql_err:
        log('ERROR', 'CM', 'Unable to retrieve error logs from SQL database! STACKTRACE: {}'.format(sql_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #all_error_logs_sql', 'message': 'Unable to retrieve error logs from SQL database! Please check logs.' }
        return jsonify(json_data)

    except Exception as plain_err:
        log('ERROR', 'CM', 'Unable to process error logs! STACKTRACE: {}'.format(plain_err.args[1]))
        
        # let webpanel know that there's an error on CM side
        json_data = { 'status': 'error #all_error_logs_plain', 'message': 'Unable to process error logs! Please check logs.' }
        return jsonify(json_data)


# main "method"
if __name__ == '__main__':
    # check to make sure the database has the required tables
    log('INFO', 'CM', 'Starting program...')
    try:
        # initiate connection
        con, cur = db_management.connect_to_db(logging, db_host, db_port, db_user, db_pass, db_name)

        # NSA'ing through tables in database
        db_management.check_tables(logging, con, cur)
    except pymysql.Error as e:
        log('ERROR', 'CM', 'Error when trying to connect to the database OR check/create table! STACKTRACE: {}'.format(e.args[1]))
        log('ERROR', 'CM', 'Force closing program...')
        exit()

    # start scraping thread job!
    log('INFO', 'CM', 'Starting scraping thread...')
    thd = Thread(target=scrape_data, args=(interval_time, ))
    thd.daemon = True
    thd.start()
    log('Scrape thread started!')

    # start Flask service
    log('Starting Flask service...')
    app.run(host=flsk_host, port=flsk_port)
