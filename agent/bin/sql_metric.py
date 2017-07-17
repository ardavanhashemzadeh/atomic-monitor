import pymysql
import time


def mb_convert(byts):
    return byts / 1024 / 1024


class SQLMetric:
	def __init__(self, _logging, _cur):
		self.logging = _logging
		self.cur = _cur

	# get SQL metrics
	def get_sql_metrics(self):
		sql_metrics = list()
		
		first_metrics = list()
		second_metrics = list()
		
		try:
			# get first metrics
			for row in self.cur.execute('SHOW GLOBAL STATUS'):
				first_metrics.append(MetricInfo(row[0], row[1]))
			
			# wait one second
			time.sleep(1)
			
			# get second metrics
			for row in self.cur.execute('SHOW GLOBAL STATUS'):
				first_metrics.append(MetricInfo(row[0], row[1]))
			
			# do math
			for i in range(0, len(first_metrics)):
				if 'BYPTES' in first_metrics.get_name():
					sql_metrics.append(MetricInfo(first_metrics.get_name(),
												  mb_convert(second_metrics.get_value() - first_metrics.get_value())))
				else:
					sql_metrics.append(MetricInfo(first_metrics.get_name(),
												  second_metrics.get_value() - first_metrics.get_value()))
		
			# SQL metrics
			return sql_metrics
		except mymysql.Error as e:
			self.logging.error('Problem when trying to retrieve metrics from SQL database! STACKTRACE: {}'.format(ex.args[1]), extra={'topic': 'SQL'})
			self.logging.error('Force closing program...', extra={'topic': 'SQL'})
            exit()
		

class MetricInfo:
	def __init__(self, _name, _value):
		self.name =_name
		self.value = _value
	
	def get_name(self):
		return self.name
	
	def get_value(self):
		return self.value
