import pymysql


def connect_to_db(logging, db_host, db_port, db_user, db_pass, db_name):
    try:
        # connect to the database
        logging.info('Connecting to the database...', extra={'topic': 'CM'})
        con = pymysql.connect(host=db_host,
                              port=int(db_port),
                              user=db_user,
                              passwd=db_pass,
                              db=db_name)
        logging.info('Successfully connected to the database!', extra={'topic': 'CM'})

        logging.info('Preparing database...', extra={'topic': 'CM'})
        cur = con.cursor()

        return con, cur
    except Exception as e:
        raise pymysql.Error(e.args[1])


def check_tables(logging, con, cur, db_prefix):
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
        logging.info('Checking {}_server table.'.format(db_prefix), extra={'topic': 'CM'})

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
        logging.info('Checking {}_log table.'.format(db_prefix), extra={'topic': 'CM'})

        # create/check ping logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_ping (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status CHAR(1),
                    ping FLOAT(100,2),
                    PRIMARY KEY(id));""".format(db_prefix))
        logging.info('Checking {}_ping table.'.format(db_prefix), extra={'topic': 'CM'})

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
        logging.info('Checking {}_memory table.'.format(db_prefix), extra={'topic': 'CM'})

        # create/check CPU logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_cpu (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status CHAR(1),
                    cpu_percent FLOAT(4,1),
                    PRIMARY KEY(id));""".format(db_prefix))
        logging.info('Checking {}_cpu table.'.format(db_prefix), extra={'topic': 'CM'})

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
        logging.info('Checking {}_network table.'.format(db_prefix), extra={'topic': 'CM'})

        # create/check load logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_load_average (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status CHAR(1),
                    1m_avg DECIMAL(5,1),
                    5m_avg DECIMAL(5,1),
                    15m_avg DECIMAL(5,1),
                    PRIMARY KEY(id));""".format(db_prefix))
        logging.info('Checking {}_load_average table.'.format(db_prefix), extra={'topic': 'CM'})

        # create/check disk logs table
        cur.execute("""CREATE TABLE IF NOT EXISTS {}_disk (
                    id BIGINT NOT NULL AUTO_INCREMENT,
                    server_id INTEGER NOT NULL,
                    stamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    status CHAR(1),
                    device VARCHAR(50),
                    percent BIGINT,
                    used BIGINT,
                    total BIGINT,
                    PRIMARY KEY(id));""".format(db_prefix))
        logging.info('Checking {}_disk table.'.format(db_prefix), extra={'topic': 'CM'})

        # submit changes to SQL server
        con.commit()
        logging.info('Database prepared!', extra={'topic': 'CM'})
    except Exception as e:
        raise pymysql.Error(e.args[1])


# retrieve online % status from SQL database
def get_online_percent(logging, cur, db_prefix, server_name, server_id):
    try:
        # retrieve data
        online = cur.execute('SELECT COUNT(status) AS online FROM {}_ping WHERE status=1;').fetchone()[0]['online']
        total = cur.execute('SELECT COUNT(status) AS total FROM {}_ping;').fetchone()[0]['total']

        # return percentage of online status
        return float(online) / float(total)
    except pymysql.Error as ex:
        logging.error('Unable to retrieve online percentage for server [{}] from SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})


# insert new ping data to SQL database
def insert_log_data(logging, cur, db_prefix, con, server_name, typ, message):
    try:
        cur.execute('INSERT INTO {}_logs (server_name, type, msg) '
                    'VALUES (?, ?, ?)'.format(db_prefix), server_name, typ, message)
        con.commit()
    except pymysql.Error as ex:
        logging.error('Unable to insert [error log] data for server [{}] to SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})


# insert new ping data to SQL database
def insert_ping_data(logging, cur, db_prefix, con, server_name, server_id, status, ping=None):
    try:
        cur.execute('INSERT INTO {}_ping (server_id, status, ping) '
                    'VALUES (?, ?, ?)'.format(db_prefix), server_id, status, ping)
        con.commit()
    except pymysql.Error as ex:
        logging.error('Unable to insert [ping] data for server [{}] to SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})


# insert new memory data to SQL database
def insert_memory_data(logging, cur, db_prefix, con, server_name, server_id, status, ram_percent=None, ram_used=None,
                       ram_total=None, swap_percent=None, swap_used=None, swap_total=None):
    try:
        cur.execute('INSERT INTO {}_memory (server_id, status, ram_percent, ram_used, ram_total, swap_percent, '
                    'swap_used, swap_total) '
                    'VALUES (?, ?, ?, ?, ?, ?, ?, ?)'.format(db_prefix), server_id, status, ram_percent, ram_used,
                    ram_total, swap_percent, swap_used, swap_total)
        con.commit()
    except pymysql.Error as ex:
        logging.error('Unable to insert [memory] data for server [{}] to SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})


# insert new CPU data to SQL database
def insert_cpu_data(logging, cur, db_prefix, con, server_name, server_id, status, cpu_percent=None):
    try:
        cur.execute('INSERT INTO {}_cpu (server_id, status, cpu_percent) '
                    'VALUES (?, ?, ?)'.format(db_prefix), server_id, status, cpu_percent)
        con.commit()
    except pymysql.Error as ex:
        logging.error('Unable to insert [cpu] data for server [{}] to SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})


# insert new network data to SQL database
def insert_net_data(logging, cur, db_prefix, con, server_name, server_id, status, name=None, sent=None, received=None):
    try:
        cur.execute('INSERT INTO {}_network (server_id, status, name, sent, received) '
                    'VALUES (?, ?, ?, ?)'.format(db_prefix), server_id, status, name, sent, received)
        con.commit()
    except pymysql.Error as ex:
        logging.error('Unable to insert [network] data for server [{}] to SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})


# insert new network data to SQL database
def insert_load_data(logging, cur, db_prefix, con, server_name, server_id, status, one_avg=None, five_avg=None,
                     fifteen_avg=None):
    try:
        cur.execute('INSERT INTO {}_load_average (server_id, status, 1m_avg, 5m_avg, 15m_avg) '
                    'VALUES (?, ?, ?, ?, ?)'.format(db_prefix), server_id, status, one_avg, five_avg, fifteen_avg)
        con.commit()
    except pymysql.Error as ex:
        logging.error('Unable to insert [load] data for server [{}] to SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})


# insert new disk data to SQL database
def insert_disk_data(logging, cur, db_prefix, con, server_name, server_id, status, device=None, percent=None, used=None,
                     total=None):
    try:
        cur.execute('INSERT INTO {}_disk (server_id, status, device, percent, used, total) '
                    'VALUES (?, ?, ?, ?, ?, ?)'.format(db_prefix), server_id, status, device, percent, used, total)
        con.commit()
    except pymysql.Error as ex:
        logging.error('Unable to insert [disk] data for server [{}] to SQL database! STACKTRACE: {}'
                      .format(server_name, ex.args[1]), extra={'topic': 'SQL'})
