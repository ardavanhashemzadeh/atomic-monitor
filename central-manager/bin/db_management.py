from datetime import datetime
import pymysql


def log(LOG_FORMAT, logger, level, typ, message):
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


class DBManagement:
    def __init__(self, _log_format, _logger):
        self.LOG_FORMAT = _log_format
        self.logger = _logger

    def connect_to_db(self, db_host, db_port, db_user, db_pass, db_name):
        try:
            # connect to the database
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Connecting to the database...')
            con = pymysql.connect(host=db_host,
                                  port=int(db_port),
                                  user=db_user,
                                  passwd=db_pass,
                                  db=db_name)
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Successfully connected to the database!')

            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Preparing database...')
            cur = con.cursor()

            return con, cur
        except Exception as e:
            raise pymysql.Error(e.args[1])

    def check_tables(self, con, cur, db_prefix):
        try:
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
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_server (
                        name VARCHAR(100) NOT NULL,
                        type CHAR(2) NOT NULL,
                        mode CHAR(1) NOT NULL,
                        hostname VARCHAR(255) NOT NULL,
                        port SMALLINT NOT NULL,
                        PRIMARY KEY(name));""".format(db_prefix))
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Checking {}_server table.'.format(db_prefix))

            # create/check error logs table
            # type:
            # 0 : warning
            # 1 : error
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_log (
                        id INTEGER NOT NULL AUTO_INCREMENT,
                        server_name VARCHAR(100) NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        type CHAR(1) NOT NULL,
                        msg VARCHAR(500) NOT NULL,
                        PRIMARY KEY(id));""".format(db_prefix))
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Checking {}_log table.'.format(db_prefix))

            # create/check ping logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_ping (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_id INTEGER NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        ping FLOAT(100,2),
                        PRIMARY KEY(id));""".format(db_prefix))
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Checking {}_ping table.'.format(db_prefix))

            # create/check memory logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_memory (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_id INTEGER NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        ram_percent FLOAT(4,1),
                        ram_used FLOAT(100,2),
                        ram_total FLOAT(100,2),
                        swap_percent FLOAT(4,1),
                        swap_used FLOAT(100,2),
                        swap_total FLOAT(100,2),
                        PRIMARY KEY(id));""".format(db_prefix))
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Checking {}_memory table.'.format(db_prefix))

            # create/check CPU logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_cpu (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_id INTEGER NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        cpu_percent FLOAT(4,1),
                        PRIMARY KEY(id));""".format(db_prefix))
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Checking {}_cpu table.'.format(db_prefix))

            # create/check network logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_network (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_id INTEGER NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        name VARCHAR(50),
                        sent BIGINT,
                        received BIGINT,
                        PRIMARY KEY(id));""".format(db_prefix))
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Checking {}_network table.'.format(db_prefix))

            # create/check load logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_load_average (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_id INTEGER NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        1m_avg FLOAT(5,2),
                        5m_avg FLOAT(5,2),
                        15m_avg FLOAT(5,2),
                        PRIMARY KEY(id));""".format(db_prefix))
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Checking {}_load_average table.'.format(db_prefix))

            # submit changes to SQL server
            con.commit()
            log(self.LOG_FORMAT, self.logger, 'INFO', 'CM', 'Database prepared!')
        except Exception as e:
            raise pymysql.Error(e.args[1])

    # insert new ping data to SQL database
    def insert_log_data(self, cur, db_prefix, con, server_name, typ, message):
        try:
            cur.execute('INSERT INTO {}_log (server_name, type, msg) VALUES (\'{}\', {}, \'{}\')'
                        .format(db_prefix, server_name, typ, message))
            con.commit()
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'CM', 'Unable to insert [error log] data for server [{}] to SQL '
                                                             'database! STACKTRACE: {}'.format(server_name, ex.args[1]))

    # insert new ping data to SQL database
    def insert_ping_data(self, cur, db_prefix, con, server_name, server_id, status, ping=0):
        try:
            cur.execute('INSERT INTO {}_ping (server_id, status, ping) VALUES ({}, {}, {})'
                        .format(db_prefix, server_id, status, ping))
            con.commit()
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'CM', 'Unable to insert [ping] data for server [{}] to SQL '
                                                             'database! STACKTRACE: {}'.format(server_name, ex.args[1]))

    # insert new memory data to SQL database
    def insert_memory_data(self, cur, db_prefix, con, server_name, server_id, status, ram_percent=0, ram_used=0,
                           ram_total=0, swap_percent=0, swap_used=0, swap_total=0):
        try:
            cur.execute('INSERT INTO {}_memory (server_id, status, ram_percent, ram_used, ram_total, swap_percent, '
                        'swap_used, swap_total) VALUES ({}, {}, {}, {}, {}, {}, {}, {})'
                        .format(db_prefix, server_id, status, ram_percent, ram_used, ram_total, swap_percent, swap_used,
                                swap_total))
            con.commit()
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'CM', 'Unable to insert [memory] data for server [{}] to SQL '
                                                             'database! STACKTRACE: {}'.format(server_name, ex.args[1]))

    # insert new CPU data to SQL database
    def insert_cpu_data(self, cur, db_prefix, con, server_name, server_id, status, cpu_percent=0):
        try:
            cur.execute('INSERT INTO {}_cpu (server_id, status, cpu_percent) VALUES ({}, {}, {})'
                        .format(db_prefix, server_id, status, cpu_percent))
            con.commit()
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'CM', 'Unable to insert [cpu] data for server [{}] to SQL '
                                                             'database! STACKTRACE: {}'.format(server_name, ex.args[1]))

    # insert new network data to SQL database
    def insert_net_data(self, cur, db_prefix, con, server_name, server_id, status, name='', sent=0, received=0):
        try:
            cur.execute('INSERT INTO {}_network (server_id, status, name, sent, received) VALUES ({}, {}, \'{}\', {}, '
                        '{})'.format(db_prefix, server_id, status, name, sent, received))
            con.commit()
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'CM', 'Unable to insert [network] data for server [{}] to SQL '
                                                             'database! STACKTRACE: {}'.format(server_name, ex.args[1]))

    # insert new network data to SQL database
    def insert_load_data(self, cur, db_prefix, con, server_name, server_id, status, one_avg=0, five_avg=0,
                         fifteen_avg=0):
        try:
            cur.execute('INSERT INTO {}_load_average (server_id, status, 1m_avg, 5m_avg, 15m_avg) VALUES ({}, {}, {}, '
                        '{}, {})'.format(db_prefix, server_id, status, one_avg, five_avg, fifteen_avg))
            con.commit()
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'CM', 'Unable to insert [load] data for server [{}] to SQL '
                                                             'database! STACKTRACE: {}'.format(server_name, ex.args[1]))
