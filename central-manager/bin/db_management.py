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
    except Exception as ex:
        print(LOG_FORMAT.format(datetime.now().strftime('%Y-%m-%d %X'),
                                'ERROR',
                                'AGENT',
                                'Unexpected error when trying to log to file! STACKTRACE: {}'.format(ex.args[0])))


class DBManagement:
    def __init__(self, _log_format, _logger):
        self.LOG_FORMAT = _log_format
        self.logger = _logger

    def connect_to_db(self, db_host, db_port, db_user, db_pass, db_name):
        try:
            # connect to the database
            log(self.LOG_FORMAT, self.logger, 'INFO', 'SQL', 'Connecting to the database...')
            con = pymysql.connect(host=db_host,
                                  port=int(db_port),
                                  user=db_user,
                                  passwd=db_pass,
                                  db=db_name)
            log(self.LOG_FORMAT, self.logger, 'INFO', 'SQL', 'Successfully connected to the database!')

            cur = con.cursor()

            return con, cur
        except pymysql.Error as ex:
            raise pymysql.Error(ex.args[1])
        except Exception as ex:
            raise Exception(ex.args[0])

    def check_tables(self, con, cur, db_prefix):
        log(self.LOG_FORMAT, self.logger, 'INFO', 'SQL', 'Preparing database...')
        log(self.LOG_FORMAT, self.logger, 'INFO', 'SQL', 'Checking all tables...')
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
            # MN : Monitoring-based Server
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

            # status:
            # 0: offline
            # 1: online
            # create/check ping logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_ping (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_name VARCHAR(100) NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        ping INT,
                        PRIMARY KEY(id));""".format(db_prefix))

            # status:
            # 0: offline
            # 1: online
            # create/check memory logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_memory (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_name VARCHAR(100) NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        ram_percent FLOAT(4,1),
                        ram_used FLOAT(100,2),
                        ram_total FLOAT(100,2),
                        swap_percent FLOAT(4,1),
                        swap_used FLOAT(100,2),
                        swap_total FLOAT(100,2),
                        PRIMARY KEY(id));""".format(db_prefix))

            # status:
            # 0: offline
            # 1: online
            # create/check CPU logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_cpu (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_name VARCHAR(100) NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        cpu_percent FLOAT(4,1),
                        PRIMARY KEY(id));""".format(db_prefix))

            # status:
            # 0: offline
            # 1: online
            # create/check network logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_network (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_name VARCHAR(100) NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        name VARCHAR(50),
                        sent BIGINT,
                        received BIGINT,
                        PRIMARY KEY(id));""".format(db_prefix))

            # status:
            # 0: offline
            # 1: online
            # create/check load logs table
            cur.execute("""CREATE TABLE IF NOT EXISTS {}_load_average (
                        id BIGINT NOT NULL AUTO_INCREMENT,
                        server_name VARCHAR(100) NOT NULL,
                        stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        status CHAR(1),
                        1m_avg FLOAT(5,2),
                        5m_avg FLOAT(5,2),
                        15m_avg FLOAT(5,2),
                        PRIMARY KEY(id));""".format(db_prefix))

            # submit changes to SQL server
            con.commit()
            log(self.LOG_FORMAT, self.logger, 'INFO', 'SQL', 'All tables checked!')
            log(self.LOG_FORMAT, self.logger, 'INFO', 'SQL', 'Database prepared!')
        except pymysql.Error as ex:
            raise pymysql.Error(ex.args[1])
        except Exception as ex:
            raise Exception(ex.args[0])

    # insert new ping data to SQL database
    def insert_log_data(self, cur, db_prefix, server_name, typ, message):
        try:
            cur.execute('INSERT INTO {}_log (server_name, type, msg) VALUES (\'{}\', {}, \'{}\')'
                        .format(db_prefix, server_name, typ, message))
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'SQL', 'Unable to insert [error log] data for server [{}] to '
                                                              'SQL database! STACKTRACE: {}'.format(server_name,
                                                                                                    ex.args[1]))

    # insert new ping data to SQL database
    def insert_ping_data(self, cur, db_prefix, server_name, status, ping=0):
        try:
            cur.execute('INSERT INTO {}_ping (server_name, status, ping) VALUES (\'{}\', {}, {})'
                        .format(db_prefix, server_name, status, ping))
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'SQL', 'Unable to insert [ping] data for server [{}] to SQL '
                                                              'database! STACKTRACE: {}'.format(server_name,
                                                                                                ex.args[1]))

    # insert new memory data to SQL database
    def insert_memory_data(self, cur, db_prefix, server_name, status, ram_percent=0, ram_used=0,
                           ram_total=0, swap_percent=0, swap_used=0, swap_total=0):
        try:
            cur.execute('INSERT INTO {}_memory (server_name, status, ram_percent, ram_used, ram_total, swap_percent, '
                        'swap_used, swap_total) VALUES (\'{}\', {}, {}, {}, {}, {}, {}, {})'
                        .format(db_prefix, server_name, status, ram_percent, ram_used, ram_total, swap_percent,
                                swap_used, swap_total))
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'SQL', 'Unable to insert [memory] data for server [{}] to SQL '
                                                              'database! STACKTRACE: {}'.format(server_name,
                                                                                                ex.args[1]))

    # insert new CPU data to SQL database
    def insert_cpu_data(self, cur, db_prefix, server_name, status, cpu_percent=0):
        try:
            cur.execute('INSERT INTO {}_cpu (server_name, status, cpu_percent) VALUES (\'{}\', {}, {})'
                        .format(db_prefix, server_name, status, cpu_percent))
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'SQL', 'Unable to insert [cpu] data for server [{}] to SQL '
                                                              'database! STACKTRACE: {}'.format(server_name,
                                                                                                ex.args[1]))

    # insert new network data to SQL database
    def insert_net_data(self, cur, db_prefix, server_name, status, name='', sent=0, received=0):
        try:
            cur.execute('INSERT INTO {}_network (server_name, status, name, sent, received) VALUES (\'{}\', {}, \'{}\','
                        ' {}, {})'.format(db_prefix, server_name, status, name, sent, received))
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'SQL', 'Unable to insert [network] data for server [{}] to SQL '
                                                              'database! STACKTRACE: {}'.format(server_name,
                                                                                                ex.args[1]))

    # insert new network data to SQL database
    def insert_load_data(self, cur, db_prefix, server_name, status, one_avg=0, five_avg=0,
                         fifteen_avg=0):
        try:
            cur.execute('INSERT INTO {}_load_average (server_name, status, 1m_avg, 5m_avg, 15m_avg) VALUES (\'{}\', {},'
                        ' {}, {}, {})'.format(db_prefix, server_name, status, one_avg, five_avg, fifteen_avg))
        except pymysql.Error as ex:
            log(self.LOG_FORMAT, self.logger, 'ERROR', 'SQL', 'Unable to insert [load] data for server [{}] to SQL '
                                                              'database! STACKTRACE: {}'.format(server_name,
                                                                                                ex.args[1]))
