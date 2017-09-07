# -*- coding: utf-8 -*-
from subprocess import check_output, CalledProcessError
from flask import Flask, jsonify, request
from configparser import ConfigParser
from warnings import filterwarnings
from urllib.request import urlopen
from datetime import datetime, timedelta
from threading import Thread
import traceback
import platform
import pymysql
import time
import json
import re
import os

from bin.objects import Server, JSONServer, Spec, Graph, Error, NetData
from bin.db_management import DBManagement


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
config.read(os.path.dirname(os.path.abspath(__file__)) + '/config.ini')
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
except IOError:
    print('CONFIG ERROR: Unable to load values from \"{}\"! STACKTRACE: \n{}'.format(err_type, traceback.format_exc()))
    print('CONFIG ERROR: Force closing program...')
    exit()


# prepare logging
logger = None
try:
    logger = open(log_file, 'a')
except IOError:
    print('FILE ERROR: Unable to open log file! STACKTRACE: \n{}'.format(traceback.format_exc()))
    print('FILE ERROR: Force closing program...')
    exit()


# perform logging
LOG_FORMAT = '{} | {:^6s} | {:^3s} | {}'


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
    except IOError:
        print(LOG_FORMAT.format(datetime.now().strftime('%Y-%m-%d %X'),
                                'ERROR',
                                'CM',
                                'Unable to log to file! STACKTRACE: \n{}'.format(traceback.format_exc())))


# setup flask
app = Flask(__name__)
db_manager = DBManagement(LOG_FORMAT, logger)


# prepare database connection
con = None
cur = None
filterwarnings('ignore', category=pymysql.Warning)


# ping test server
def ping_server(host):
    # ping server
    try:
        if 'Windows' in platform.platform():
            ping_result = check_output(['ping', '-n', '1', '-w', '1', '{}'.format(host)]).decode("utf-8")
        else:
            ping_result = check_output(['ping', '-c', '1', '-W', '1', '{}'.format(host)]).decode("utf-8")

        if 'time<' in ping_result:
            ping_result = re.search('time<([\d.]+)', ping_result).group(1)
        elif 'time=' in ping_result:
            ping_result = re.search('time=([\d.]+)', ping_result).group(1)
        else:
            ping_result = -1
        return ping_result
    except CalledProcessError:
        return -1


# scrape data from each agent (server)
def scrape_data(time_interval):
    while True:
        try:
            count = 0

            # get list of servers
            cur.execute('SELECT * FROM {}_server'.format(db_prefix))
            for row in cur.fetchall():

                # go through each server and scrape data
                scrape_data_server(Server(row[0], row[1], row[2], row[3], row[4], int(row[5])))
                count += 1

            # commit changes to database
            con.commit()

            log('INFO', 'CM', 'Successfully retrieved and logged data on {} server(s)!'.format(count))

        except pymysql.Error:
            log('ERROR', 'SQL', 'Problem when trying to retrieve data from SQL database! STACKTRACE: \n{}'
                .format(traceback.format_exc()))
            log('ERROR', 'CM', 'Force closing program...')
            exit()
        time.sleep(time_interval)


# process through a server in thread mode
def scrape_data_server(server):
    try:
        ping_result = ping_server(server.get_host())
        if ping_result is not -1:
            try:
                # sniff up data from a server
                with urlopen('http://{}:{}/all'.format(server.get_host(), server.get_port())) as url:
                    data = json.loads(url.read().decode())

                    # insert data to SQL db
                    db_manager.insert_ping_data(cur, db_prefix, server.get_id(), 1, ping_result)

                    if float(ping_result) > 200.0:
                        db_manager.insert_log_data(cur, server.get_id(), 0, 'Slow ping response: {} ms'.format(
                            ping_result))

                    # insert ram data to SQL db
                    db_manager.insert_memory_data(cur, db_prefix, server.get_id(), 1,
                                                  data['memory']['ram']['percent'],
                                                  data['memory']['ram']['used'],
                                                  data['memory']['ram']['total'],
                                                  data['memory']['swap']['percent'],
                                                  data['memory']['swap']['used'],
                                                  data['memory']['swap']['total'])

                    # log if RAM/swap is 90% or above
                    if data['memory']['ram']['percent'] >= 90:
                        db_manager.insert_log_data(cur, server.get_id(), 0, 'High RAM usage: {}%'.format(
                            data['memory']['ram']['percent']))
                    if data['memory']['swap']['percent'] >= 90:
                        db_manager.insert_log_data(cur, server.get_id(), 0, 'High swap usage: {}%'.format(
                            data['memory']['swap']['percent']))

                    # insert CPU data to SQL db
                    db_manager.insert_cpu_data(cur, db_prefix, server.get_id(), 1,
                                               data['cpu']['percent'])

                    # log if CPU is 90% or above
                    if data['cpu']['percent'] >= 90:
                        db_manager.insert_log_data(cur, server.get_id(), 0, 'High CPU usage: {}%'.format(
                            data['cpu']['percent']))

                    # insert network data to SQL db
                    net_data = []
                    for net_nic in data['network']:
                        net_data.append(NetData(net_nic['name'], net_nic['sent'], net_nic['recv']))
                    db_manager.insert_net_data(cur, db_prefix, server.get_id(), 1, net_data)

                    # insert load average data to SQL db
                    db_manager.insert_load_data(cur, db_prefix, server.get_id(), 1,
                                                data['load']['onemin'],
                                                data['load']['fivemin'],
                                                data['load']['fifteenmin'])

                    # log if load average is 1.00 or above
                    if data['load']['onemin'] != "NULL":
                        if float(data['load']['onemin']) > 1.00:
                            db_manager.insert_log_data(cur, server.get_id(), 0, 'High 1m load usage: {}'.format(
                                data['load']['onemin']))
                        elif float(data['load']['fivemin']) > 1.00:
                            db_manager.insert_log_data(cur, server.get_id(), 0, 'High 5m load usage: {}'.format(
                                data['load']['fivemin']))
                        elif float(data['load']['fifteenmin']) > 1.00:
                            db_manager.insert_log_data(cur, server.get_id(), 0, 'High 15m load usage: {}'.format(
                                data['load']['fifteenmin']))

            except pymysql.Error:
                log('ERROR', 'SCRAPE', 'Unable to access server [{} ({})]! Please make sure the port is open on that'
                                       ' server!'.format(server.get_name(), server.get_id()))

        else:
            db_manager.insert_ping_data(cur, db_prefix, server.get_id(), 0)
            db_manager.insert_memory_data(cur, db_prefix, server.get_id(), 0)
            db_manager.insert_cpu_data(cur, db_prefix, server.get_id(), 0)
            db_manager.insert_net_data(cur, db_prefix, server.get_id(), 0)
            db_manager.insert_load_data(cur, db_prefix, server.get_id(), 0)
            db_manager.insert_log_data(cur, db_prefix, server.get_id(), 1, 'Server not responding to ping')
            log('WARN', 'SCRAPE', 'Server [{}] is not responding, skipping...'.format(server.get_name()))

    except Exception:
        traceback.format_exc()
        log('ERROR', 'SQL', 'Unable to retrieve data for server [{} ({})] to SQL database! STACKTRACE: \n{}'.format(
            server.get_name(), server.get_id(), traceback.format_exc()))


# retrieve now status for index.html page
@app.route('/home')
def web_home():
    # retrieve list of servers
    servers = list()
    try:
        cur.execute('SELECT * FROM {}_server'.format(db_prefix))
        for row in cur.fetchall():
            json_serv = JSONServer(row[0], row[1], row[2], row[3], row[4], int(row[5]))

            # check if server is online & responding
            ping_result = ping_server(json_serv.get_host())
            if ping_result is not -1:

                # retrieve now status from the agent
                with urlopen('http://{}:{}/now'.format(json_serv.get_host(), json_serv.get_port())) as url:
                    r = json.loads(url.read().decode())
                    os_type = r['os']
                    cpu_percent = r['cpu']['percent']
                    ram_percent = r['ram']['percent']
                    swap_percent = r['swap']['percent']
                    boot_timestamp = r['boot']['timestamp']
                    load_1m = r['load']['onemin']
                    load_5m = r['load']['fivemin']
                    load_15m = r['load']['fifteenmin']
                    disk_status = 'Good'
                    disk_percent = 0
                    for disk in r['disks']:
                        if 70 <= disk['percent'] < 90:
                            disk_status = "Device '{}' at {}% full".format(disk['name'], disk['percent'])
                            disk_percent = disk['percent']
                            break
                        elif disk['percent'] >= 90:
                            disk_status = "Device '{}' at {}% full".format(disk['name'], disk['percent'])
                            disk_percent = disk['percent']
                            break

                    # assign them to HomeServer object
                    json_serv.set_specs(True, os_type, boot_timestamp, ping_result, cpu_percent, ram_percent,
                                        swap_percent, load_1m, load_5m, load_15m, disk_status, disk_percent)

                    # add to the list
                    servers.append(json_serv)

            else:
                # assign empty values to HomeServer object
                json_serv.set_specs(False, 'times', 0, 0, 0, 0, 0, 0, 0, 0, 'Server not responding', 0)

                # add to the list
                servers.append(json_serv)

        # convert HomeServer list object into json_data
        json_data = {
            'status': 'good',
            'data': []
        }
        for json_serv in servers:
            json_data['data'].append(json_serv.__dict__)

        # print json data
        return jsonify(json_data)

    except pymysql.Error:
        log('ERROR', 'CM', 'Unable to retrieve list of servers from SQL database! STACKTRACE: \n{}'
            .format(traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #home_sql', 'message': 'Unable to retrieve list of servers from SQL database!'
                                                             ' Please check logs.'}
        return jsonify(json_data)

    except Exception:
        log('ERROR', 'CM', 'Unable to process through list of servers! STACKTRACE: \n{}'.format(traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #home_plain', 'message': 'Unable to process through list of servers! Please '
                                                               'check logs.'}
        return jsonify(json_data)


@app.route('/server_names')
def web_server_names():
    # retrieve list of server names
    try:
        server_names = []
        cur.execute('SELECT id, name FROM {}_server'.format(db_prefix))
        for row in cur.fetchall():
            server_names.append([int(row[0]), row[1]])
        
        # convert to json data
        json_data = {
            'status': 'good',
            'data': []
        }
        for server_name in server_names:
            json_data['data'].append(server_name)

        # print json data
        return jsonify(json_data)

    except pymysql.Error:
        log('ERROR', 'CM', 'Unable to retrieve list of server names from SQL database! STACKTRACE: \n{}'
            .format(traceback.format_exc()))

        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #server_names_sql', 'message': 'Unable to retrieve list of server names from SQL '
                                                                     'database! Please check logs.'}
        return jsonify(json_data)

    except Exception:
        log('ERROR', 'CM', 'Unable to process through list of servers! STACKTRACE: \n{}'.format(traceback.format_exc()))

        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #server_names_plain', 'message': 'Unable to process through list of server names!'
                                                                       ' Please check logs.'}
        return jsonify(json_data)


@app.route('/graph/<server_id>/')
def web_graph(server_id):
    timeline_limit = request.args.get('limit', 1800, type=int)

    # create datetime ranges
    timeline_start = datetime.now() - timedelta(seconds=timeline_limit)
    timeline_end = datetime.now()
    str_start = timeline_start.strftime('%Y-%m-%d %H:%M:%S')
    str_end = timeline_end.strftime('%Y-%m-%d %H:%M:%S')

    try:
        # retrieve hostname & port for server
        cur.execute('SELECT name, type, mode, hostname, port FROM {}_server WHERE id={}'.format(db_prefix, server_id))
        row = cur.fetchone()

        name = row[0]
        typeserv = row[1]
        mode = row[2]
        hostname = row[3]
        port = row[4]

        # create graph object
        server_graph = Graph(server_id, name, typeserv, mode)

        # check if server is online & responding
        ping_result = ping_server(hostname)
        if ping_result is not -1:
            server_graph.set_online(True)
        else:
            server_graph.set_online(False)

        # retrieve now status
        cpu_current, ram_current, ram_max, swap_current, swap_max, load_1m, load_5m, load_15m, disk_device_list, \
            disk_data_list = 0, 0,  0, 0, 0, 0, 0, 0, [], []
        if ping_result is not -1:
            with urlopen('http://{}:{}/now'.format(hostname, port)) as url:
                r = json.loads(url.read().decode())
                cpu_current = r['cpu']['percent']
                ram_current = r['ram']['percent']
                ram_max = r['ram']['total']
                swap_current = r['swap']['percent']
                swap_max = r['swap']['total']
                load_1m = r['load']['onemin']
                load_5m = r['load']['fivemin']
                load_15m = r['load']['fifteenmin']
                for disk in r['disks']:
                    disk_device_list.append(disk['name'])
                    disk_data_list.append(disk['percent'])

        # retrieve timestamps
        timestamps = []
        cur.execute('SELECT stamp FROM {}_cpu WHERE server_id={} AND stamp BETWEEN \'{}\' AND \'{}\';'
                    .format(db_prefix, server_id, str_start, str_end))
        for row in cur.fetchall():
            timestamps.append(row[0])
        server_graph.set_timeline(timestamps)

        # retrieve CPU graph data
        cpu_data = []
        cur.execute('SELECT cpu_percent FROM {}_cpu WHERE server_id={} AND stamp BETWEEN \'{}\' AND \'{}\';'
                    .format(db_prefix, server_id, str_start, str_end))
        for row in cur.fetchall():
            cpu_data.append(row[0])
        server_graph.set_graph_cpu(cpu_current, 100, cpu_data)

        # retrieve RAM & swap graph data
        ram_data = []
        swap_data = []
        cur.execute('SELECT ram_used, swap_used FROM {}_memory WHERE server_id={} AND stamp BETWEEN \'{}\' AND \'{}\';'
                    .format(db_prefix, server_id, str_start, str_end))
        for row in cur.fetchall():
            ram_data.append(row[0])
            swap_data.append(row[1])
        server_graph.set_graph_ram(ram_current, ram_max, ram_data)
        server_graph.set_graph_swap(swap_current, swap_max, swap_data)

        # retrieve load average graph data
        load_max = 0
        load_data = []
        cur.execute('SELECT 1m_avg, 5m_avg, 15m_avg FROM {}_load_average WHERE server_id={} AND stamp BETWEEN \'{}\' '
                    'AND \'{}\';'.format(db_prefix, server_id, str_start, str_end))
        for row in cur.fetchall():
            if row[0] > load_max:
                load_max = row[0]
            if row[1] > load_max:
                load_max = row[0]
            if row[2] > load_max:
                load_max = row[0]
            load_data.append([row[0], row[1], row[2]])
        server_graph.set_graph_load(load_1m, load_5m, load_15m, load_max, load_data)

        # retrieve network download/upload graph data
        netdown_max = 0
        netdown_data = []
        netup_max = 0
        netup_data = []
        cur.execute('SELECT id FROM {}_network WHERE server_id={} AND stamp BETWEEN \'{}\' AND \'{}\';'
                    .format(db_prefix, server_id, str_start, str_end))
        for row in cur.fetchall():
            device_id = row[0]
            cur.execute('SELECT name, sent, received FROM {}_network_device WHERE id={}'.format(db_prefix, device_id))
            curr_netdown_data = []
            curr_netup_data = []
            for row2 in cur.fetchall():
                curr_netdown_data.append([row2[0], row2[1]])
                curr_netup_data.append([row2[0], row2[2]])

                if netup_max < row2[1]:
                    netup_max = row2[1]
                if netdown_max < row2[2]:
                    netdown_max = row2[2]
            netdown_data.append(curr_netdown_data)
            netup_data.append(curr_netup_data)
        server_graph.set_graph_netup(netup_max, netup_data)
        server_graph.set_graph_netdown(netdown_max, netdown_data)

        # retrieve ping data
        ping_max = 0
        ping_data = []
        cur.execute('SELECT ping FROM {}_ping WHERE server_id={} AND stamp BETWEEN \'{}\' AND \'{}\';'
                    .format(db_prefix, server_id, str_start, str_end))
        for row in cur.fetchall():
            ping_data.append(row[0])
        server_graph.set_graph_ping(ping_max, ping_data)

        # retrieve disk progressbar data
        server_graph.set_progbar_disks(disk_device_list, disk_data_list)

        # convert HomeServer list object into json_data
        json_data = {'status': 'good', 'data': server_graph.__dict__}

        # print json data
        return jsonify(json_data)

    except pymysql.Error:
        log('ERROR', 'CM', 'Unable to retrieve info for server ID [{}] from SQL database! STACKTRACE: \n{}'
            .format(server_id, traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #graph_sql', 'message': 'Unable to retrieve info for server ID [{}] from SQL '
                                                              'database! Please check logs.'.format(server_id)}
        return jsonify(json_data)

    except Exception:
        log('ERROR', 'CM', 'Unable to process graph info for server ID [{}]! STACKTRACE: \n{}'
            .format(server_id, traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #graph_plain', 'message': 'Unable to process graph info for server ID [{}]! '
                                                                'Please check logs.'.format(server_id)}
        return jsonify(json_data)


@app.route('/specs/<server_id>')
def web_specs(server_id):
    # retrieve hostname & port for server
    try:
        cur.execute('SELECT hostname, port FROM {}_server WHERE id=%d'.format(db_prefix), server_id)
        row = cur.fetchone()
        hostname = row[0]
        port = row[1]

        # check if server is online & responding
        ping_result = ping_server(hostname)
        if ping_result is -1:
            # create json data
            json_data = {'status': 'error #specs_offline',
                         'message': 'Unable to retrieve hardware specifications for server ID [{}] because the server '
                                    'is not responding to ping! Either it\'s broken or offline.'.format(server_id)}
            
            # let webpanel know that the agent server can't be reached
            return jsonify(json_data)
        else:
            # retrieve hardware specifications
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
                             [r['load']['1min'], r['load']['5min'], r['load']['15min']])

            # calculate server's availability
            cur.execute('''SELECT alive.num / total.num * 100.0 as available
                        FROM ( SELECT COUNT(status) as num FROM {0}_ping WHERE status = 1  ) alive
                        JOIN ( SELECT COUNT(status) as num FROM {0}_ping                   ) total;'''
                        .format(db_prefix))
            specs.set_availability(round(float(cur.fetchone()[0]), 1))

            # convert to json data
            json_data = {'status': 'good', 'data': specs.__dict__}
            print(json_data)

            # print json data
            return jsonify(json_data)

    except pymysql.Error:
        log('ERROR', 'CM', 'Unable to retrieve info for server ID [{}] from SQL database! STACKTRACE: \n{}'
            .format(server_id, traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #graph_sql', 'message': 'Unable to retrieve info for server ID [{}] from SQL '
                                                              'database! Please check logs.'.format(server_id)}
        return jsonify(json_data)

    except Exception:
        log('ERROR', 'CM', 'Unable to process graph info for server ID [{}]! STACKTRACE: \n{}'
            .format(server_id, traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #graph_plain', 'message': 'Unable to process graph info for server ID [{}]! '
                                                                'Please check logs.'.format(server_id)}
        return jsonify(json_data)


@app.route('/server_logs/<server_id>/')
def web_server_logs(server_id):
    level = request.args.get('level', -1, type=int)
    count = request.args.get('count', -1, type=int)
    search_for = request.args.get('search_for', '', type=str)
    filter_out = request.args.get('filter_out', '', type=str)

    errors = list()
    # retrieve errors
    try:
        if level is -1:
            sql_statement = '(SELECT * FROM {}_log WHERE server_id=\'{}\''.format(db_prefix, server_id)
            if search_for is not '':
                sql_statement += ' AND msg LIKE \'{}\''.format('%{}%'.format(search_for))
            if filter_out is not '':
                sql_statement += ' AND msg NOT LIKE \'{}\''.format('%{}%'.format(filter_out))
            if count is -1:
                sql_statement += ' ORDER BY id DESC) ORDER BY id DESC'
            else:
                sql_statement += ' ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(count)
        else:
            sql_statement = '(SELECT * FROM {}_log WHERE server_id=\'{}\' AND type={}'.format(db_prefix, server_id,
                                                                                              level)
            if search_for is not '':
                sql_statement += ' AND msg LIKE \'{}\''.format('%{}%'.format(search_for))
            if filter_out is not '':
                sql_statement += ' AND msg NOT LIKE \'{}\''.format('%{}%'.format(filter_out))
            if count is -1:
                sql_statement += ' ORDER BY id DESC) ORDER BY id DESC'
            else:
                sql_statement += ' ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(count)

        cur.execute(sql_statement)

        for row in cur.fetchall():
            errors.append(Error(row[3], row[1], row[4], row[2]))

        # convert to json
        json_data = {
            'status': 'good',
            'data': []
        }
        for error in errors:
            json_data['data'].append(error.__dict__)

        # print json data
        return jsonify(json_data)

    except pymysql.Error:
        log('ERROR', 'CM', 'Unable to retrieve error logs for server ID [{}] from SQL database! STACKTRACE: \n{}'
            .format(server_id, traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #server_error_logs_sql',
                     'message': 'Unable to retrieve error logs for server ID [{}] from SQL database! Please check '
                                'logs.'.format(server_id)}
        return jsonify(json_data)

    except Exception:
        log('ERROR', 'CM', 'Unable to process error logs for server ID [{}]! STACKTRACE: \n{}'
            .format(server_id, traceback.format_exc()))
        
        # let webpanel know that there's an error on CM side
        json_data = {'status': 'error #server_error_logs_plain', 'message': 'Unable to process error logs for server '
                                                                            'ID [{}]! Please check logs.'
            .format(server_id)}
        return jsonify(json_data)


@app.route('/all_logs/')
def web_all_logs():
    server_id = int(request.args.get('id', -1, type=int))
    level = int(request.args.get('level', -1, type=int))
    limit = int(request.args.get('limit', 50, type=int))
    search_for = request.args.get('search_for', '', type=str)
    filter_out = request.args.get('filter_out', '', type=str)

    # TODO set anti-hacking programs to prevent bad values for server_id, level, limit, search_for, & filter_out

    server_names = {}
    errors = list()
    # retrieve errors
    try:
        cur.execute('SELECT id, name FROM {}_server'.format(db_prefix))

        for row in cur.fetchall():
            server_names[int(row[0])] = row[1]

        if server_id > 0:
            if level is -1:
                sql_statement = '(SELECT * FROM {}_log WHERE server_id=\'{}\''.format(db_prefix, server_id)
                if search_for is not '':
                    sql_statement += ' AND msg LIKE \'{}\''.format('%{}%'.format(search_for))
                if filter_out is not '':
                    sql_statement += ' AND msg NOT LIKE \'{}\''.format('%{}%'.format(filter_out))
                sql_statement += ' ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(limit)
            else:
                sql_statement = '(SELECT * FROM {}_log WHERE server_id=\'{}\' AND type={}'.format(db_prefix, server_id,
                                                                                                  level)
                if search_for is not '':
                    sql_statement += ' AND msg LIKE \'{}\''.format('%{}%'.format(search_for))
                if filter_out is not '':
                    sql_statement += ' AND msg NOT LIKE \'{}\''.format('%{}%'.format(filter_out))
                sql_statement += ' ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(limit)
        else:
            if level is -1:
                sql_statement = '(SELECT * FROM {}_log'.format(db_prefix)
                if search_for is not '':
                    sql_statement += 'WHERE msg LIKE \'{}\''.format('%{}%'.format(search_for))
                if filter_out is not '':
                    if 'WHERE' not in sql_statement:
                        sql_statement += ' WHERE'
                    sql_statement += ' AND msg NOT LIKE \'{}\''.format('%{}%'.format(filter_out))
                sql_statement += ' ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(limit)
            else:
                sql_statement = '(SELECT * FROM {}_log WHERE type={}'.format(db_prefix, level)
                if search_for is not '':
                    sql_statement += ' AND msg LIKE \'{}\''.format('%{}%'.format(search_for))
                if filter_out is not '':
                    sql_statement += ' AND msg NOT LIKE \'{}\''.format('%{}%'.format(filter_out))
                sql_statement += ' ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(limit)

        cur.execute(sql_statement)

        for row in cur.fetchall():
            errors.append(Error(row[3], server_names[int(row[1])], row[4], row[2]))

        # convert to json
        json_data = {
            'status': 'good',
            'data': []
        }
        for error in errors:
            json_data['data'].append(error.__dict__)

        # print json data
        return jsonify(json_data)

    except pymysql.Error:
        log('ERROR', 'CM', 'Unable to retrieve error logs from SQL database! STACKTRACE: \n{}'
            .format(traceback.format_exc()))
        
        # let web panel know that there's an error on CM side
        json_data = {'status': 'error #all_error_logs_sql', 'message': 'Unable to retrieve error logs from SQL '
                                                                       'database! Please check logs.'}
        return jsonify(json_data)

    except Exception:
        log('ERROR', 'CM', 'Unable to process error logs! STACKTRACE: \n{}'.format(traceback.format_exc()))
        
        # let web panel know that there's an error on CM side
        json_data = {'status': 'error #all_error_logs_plain', 'message': 'Unable to process error logs! Please check '
                                                                         'logs.'}
        return jsonify(json_data)


# main "method"
if __name__ == '__main__':
    # check to make sure the database has the required tables
    log('INFO', 'CM', 'Starting program...')
    try:
        # initiate connection
        con, cur = db_manager.connect_to_db(db_host, db_port, db_user, db_pass, db_name)

        # NSA'ing through tables in database
        db_manager.check_tables(con, cur, db_prefix)
    except pymysql.Error as e:
        log('ERROR', 'SQL', 'Error when trying to connect to the database OR check/create table! STACKTRACE: \n{}'
            .format(traceback.format_exc()))
        log('ERROR', 'CM', 'Force closing program...')
        exit()

    # start scraping thread job!
    log('INFO', 'CM', 'Starting scraping thread...')
    thd = Thread(target=scrape_data, args=(interval_time, ))
    thd.daemon = True
    thd.start()
    log('INFO', 'CM', 'Scrape thread started!')

    # start Flask service
    log('INFO', 'CM', 'Starting Flask service...')
    app.run(host=flsk_host, port=flsk_port)
