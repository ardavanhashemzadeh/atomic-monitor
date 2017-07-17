# -*- coding: utf-8 -*-
from configparser import ConfigParser
from warnings import filterwarnings
from datetime import datetime
from threading import Thread
from flask import Flask, jsonify
from urllib.request import urlopen
import pymysql
import pexpect
import json

from bin.server_obj import Server
from bin.errorlog_obj import ErrorLog
import bin.db_management as db_management


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
    db_pass = config.get('Storage', 'Pass')
    err_type = 'Storage > Database'
    db_name = config.get('Storage', 'Database')
    err_type = 'Storage > Prefix'
    db_prefix = config.get('Storage', 'Prefix')

    # collector
    interval_time = config.getint('Collector', 'Interval')

    # flask connection info
    flsk_host = config.get('UI_Feeder', 'Host')
    flsk_port = config.getint('UI_Feeder', 'Port')
except IOError as e:
    print('CONFIG ERROR: Unable to load values from \"{}\"! STACKTRACE: {}'.format(err_type, e.args[1]))
    print('CONFIG ERROR: Force closing program...')
    exit()


# prepare logging
try:
	logger = logging.getLogger('AtomicMonitor Central-Manager')
	logger.setLevel(logging.DEBUG)
	logger.addHandler(logging.handlers.RotatingFileHandler(log_file, maxBytes=log_size_limit, backupCount=log_file_limit))
	ch = logging.StreamHandler()
	ch.setFormatter(logging.Formatter('%(asctime)s | %(levelname)-8s | %(topic)-5s | %(message)s'))
	logger.addHandler(ch)
except IOError as e:
    print('FILE ERROR: Unable to prepare log file! STACETRACE: {}'.format(e.args[1]))
    print('FILE ERROR: Force closing program...')
    exit()


# setup flask
app = Flask(__name__)


# prepare database connection
con = None
cur = None
filterwarnings('ignore', category = pymysql.Warning)


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
                            insert_ping_data(serv.id, 1, ping_result)
                            if ping_result > 200:
                                insert_log_data(logging, con, cur, serv.name, 0, 
												'Slow ping response: {} ms'.format(ping_result))

                            # insert ram data to SQL db
                            insert_memory_data(logging, 
											   con, 
											   cur,
											   serv.id,
                                               1,
                                               data['memory']['ram']['percent_used'],
                                               data['memory']['ram']['used'],
                                               data['memory']['ram']['total'],
                                               data['memory']['swap']['percent_used'],
                                               data['memory']['swap']['used'],
                                               data['memory']['swap']['total'])
                            if data['memory']['ram']['percent_used'] >= 90:
                                insert_log_data(logging, 
												con, 
												cur, 
												serv.name, 
												0, 
												'High RAM usage: {}%'.format(data['memory']['ram']['percent_used']))

                            # insert CPU data to SQL db
                            insert_cpu_data(logging, 
											con, 
											cur, 
											serv.id,
                                            1,
                                            data['cpu']['percent_used'])
                            if data['cpu']['percent_used'] >= 90:
                                insert_log_data(logging, 
												con, 
												cur, 
												serv.name, 
												0, 
												'High CPU usage: {}%'.format(data['cpu']['percent_used']))

                            # insert network data to SQL db
                            for net_nic in data['network']:
                                insert_net_data(logging, 
												con, 
												cur, 
												serv.id,
                                                1,
                                                net_nic['name'],
                                                net_nic['mb_sent'],
                                                net_nic['mb_received'])

                            # insert load average data to SQL db
                            insert_load_data(logging, 
											con, 
											cur, 
											serv.id,
                                            1,
                                            data['load']['1min'],
                                            data['load']['5min'],
                                            data['load']['15min'])
                            if data['load']['1min'] is not None:
                                if data['load']['1min'] > 1.00:
                                    insert_log_data(logging, 
													con, 
													cur, 
													serv.name, 
													0,
                                                    'High 1m load usage: {}'.format(data['load']['1min']))
                                elif data['load']['5min'] > 1.00:
                                    insert_log_data(logging, 
													con, 
													cur, 
													serv.name, 
													0,
                                                    'High 5m load usage: {}'.format(data['load']['5min']))
                                elif data['load']['15min'] > 1.00:
                                    insert_log_data(logging, 
													con, 
													cur, 
													serv.name, 
													0,
                                                    'High 15m load usage: {}'.format(data['load']['15min']))

                            # insert disk data to SQL db
                            for disk in data['disks']['list']:
                                insert_disk_data(logging, 
												 con, 
												 cur, 
												 serv.id,
                                                 1,
                                                 disk['device'],
                                                 disk['percent_used'],
                                                 disk['used'],
                                                 disk['total'])
                                if disk['percent_used'] > 90:
                                    insert_log_data(logging, 
													con, 
													cur, 
													serv.name, 
													0,
                                                    'High disk space usage: {}%'.format(disk['percent_used']))
                            
                            # insert SQL metrics to SQL db
                            if data['sql_metric']['enabled'] is True:
                                for metric in data['sql_metric']['list']:
                                    

                            logging.info('Retrieved and logged data for server [{}]!'.format(serv.name), extra={'topic': 'CM'})
                    except pymysql.Error:
						logging.error('Unable to access server [{}]! Please make sure the port is open on that '
									  'server!'.format(serv.name), extra={'topic': 'AGENT'})
                else:
                    insert_ping_data(serv.id, 0)
                    insert_memory_data(serv.id, 0)
                    insert_cpu_data(serv.id, 0)
                    insert_net_data(serv.id, 0)
                    insert_load_data(serv.id, 0)
                    insert_disk_data(serv.id, 0)
                    insert_log_data(serv.name, 1, 'Server not responding to ping')
					logging.warning('Server [{}] is not responding, skipping...'.format(serv.name), extra={'topic': 'CM'})
        except pymysql.Error as ex:
			logging.error('Problem when trying to retrieve data from SQL database! STACKTRACE: {}'.format(ex.args[1]), extra={'topic': 'SQL'})
			logging.error('Force closing program...', extra={'topic': 'SQL'})
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
			
			logging.info('Retrieved now status for host {}:{} for IP: {}'.format(hostname, port, request.remote_addr), extra={'topic': 'CM'})

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
        for row in cur.execute('SELECT * FROM {}_server'.format(db_prefix)):
            servers.append(Server(row[0], row[1], row[2], row[3], row[4], row[5]))
        names, types, modes, hosts, ports = [], [], [], [], []
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
		
		logging.info('Retrieved all servers data for IP: {}'.format(request.remote_addr), extra={'topic': 'CM'})

        # print json data
        return jsonify(json_data)
    except pymysql.Error as ex:
		logging.error('Error when trying to retrieve data from the database! STACKTRACE: {}'.format(ex.args[1]), extra={'topic': 'SQL'})
		logging.error('Force closing program...', extra={'topic': 'SQL'})
        exit()


# start Flask service: retrieve latest errors
@app.route('/errors/<count>')
def web_errors(count):
    errors = list()
    # access database to retrieve errors
    try:
        # retrieve data
        for row in cur.execute('(SELECT * FROM {}_log ORDER BY id DESC LIMIT {}) ORDER BY id DESC'.format(db_prefix,
                                                                                                           count)):
            errors.append(ErrorLog(row[1], row[2], row[3], row[4]))
        servernames, timestamps, types, msgs = [], [], [], []
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
		
		logging.info('Retrieved all {} error data for IP: {}'.format(count, request.remote_addr), extra={'topic': 'CM'})

        # print json data
        return jsonify(json_data)
    except pymysql.Error as ex:
        logging.error('Error when trying to retrieve data from the database! STACKTRACE: {}'.format(ex.args[1]), extra={'topic': 'SQL'})
		logging.error('Force closing program...', extra={'topic': 'SQL'})
        exit()


# main "method"
if __name__ == '__main__':
    # check to make sure the database has the required tables
	logging.info('Starting program...', extra={'topic': 'CM'})
    try:
		# initiate connection
		con, cur = db_management.connect_to_db(logging, db_host, db_port, db_user, db_pass, db_name)
	
		# NSA'ing through tables in database
		db_management.check_tables(logging, con, cur)
    except pymysql.Error as e:
		logging.error('Error when trying to connect to the database OR check/create table! STACKTRACE: {}'.format(ex.args[1]), extra={'topic': 'SQL'})
		logging.error('Force closing program...', extra={'topic': 'SQL'})
        exit()

    # start scraping thread job!
	logging.info('Starting scraping thread...', extra={'topic': 'CM'})
    #thd = Thread(target=scrape_data, args=(interval_time, ))
    #thd.daemon = True
    #thd.start()
	logging.info('Scrape thread started!', extra={'topic': 'CM'})

    # start Flask service
	logging.info('Starting Flask service...', extra={'topic': 'CM'})
app.run(host=flsk_host, port=flsk_port)