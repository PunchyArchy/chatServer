import psycopg2
import wsettings as s
from datetime import datetime

class WSQLshell():
	def __init__(self, dbname, user, password, host):
		self.dbname = dbname
		self.user = user
		self.password = password
		self.host = host
		self.conn = psycopg2.connect(dbname = self.dbname, user = self.user,
			password = self.password, host = self.host)

	def get_cursor(self):
		'''Возвращает курсор'''
		return self.cursor

	def get_all(self, tablename):
		'''Возвращает все содержимое таблицы (tablename)'''
		cursor = self.create_get_cursor()
		cursor.execute('select * from {}'.format(tablename))
		records = cursor.fetchall()
		cursor.close()
		return records

	def get_all_ident(self, tablename, ident):
		cursor = self.create_get_cursor()
		cursor.execute('select * from {} where {}'.format(tablename, ident))
		records = cursor.fetchall()
		cursor.close()
		return records

	def get_all_2idents(self, tablename, ident1, ident2):
		cursor = self.create_get_cursor()
		cursor.execute('select * from {} where {}'.format(tablename,
			ident1, ident2))
		records = cursor.fetchall()
		cursor.close()
		return records

	def get_special_ident(self, tablename, spec, ident):
		'''Возвращает spec значение по равенству ident из таблицы tablename'''
		cursor = self.create_get_cursor()
		cursor.execute('select {} from {} where {}'.format(spec,
			tablename, ident))
		record = cursor.fetchall()
		cursor.close()
		return record

	def get_special_2idents(self, tablename, spec, ident1, ident2):
		'''Возвращает spec значение по двум равенствам ident1 и
		ident2 из таблицы tablename'''
		cursor = self.create_get_cursor()
		cursor.execute('select {} from {} where {} and {}'.format(spec,
			tablename, ident1, ident2))
		record = cursor.fetchall()
		cursor.close()
		return record

	def check_presence(self, value, tablename, column):
		'''Проверяет присутствие значения (value) в
		таблице (tablename), в столбце (column)'''
		print('Проверяю наличие',value,'в',tablename,'pos',column)
		records = self.get_all(tablename)
		for record in records:
			if str(value) == str(record[column]):
				#print('Yep')
				return True

	def create_get_cursor(self, mode=1):
		cursor = self.conn.cursor()
		if mode == 2:
			return cursor, self.conn
		else:
			return cursor

	def check_car_inside(self, carnum, tablename):
		'''Проверяет находится ли машина на территории предприятия'''
		#self.check_presence(carnum, tablename, column)
		cursor = self.create_get_cursor()
		cursor.execute("select * from {} where НомерАвто='{}' and НаТерритории='yes'".format(tablename,
		carnum))
		record = cursor.fetchall()
		#print('record-',record)
		cursor.close()
		if len(record) == 0:
			return False
		else:
			return True

		#if record[0][tablename] == 'yes':
			#return True

	def get_maxid(self, tablename):
		cursor = self.create_get_cursor()
		cursor.execute("select max(id) from {}".format(tablename))
		record = cursor.fetchall()
		cursor.close()
		return record

	def check_access(self, rfid):
		'''Проверяет, разрешается ли машине въезд'''
		if self.check_presence(rfid, 'Авто', 1):
			return True

	def add_weight(self, name, weight, carnum):
		cursor,conn = self.create_get_cursor(mode=2)
		cursor.execute(
			"update {} set {}='{}' where НомерАвто='{}' and НаТерритории='Yes'".format(
			s.book, name, weight, carnum))
		conn.commit()

	def create_str(self, tablename, template, values):
		'''Создает новую строку в БД, получает кортеж-шаблон, и кортеж
		значений'''
		cursor,conn = self.create_get_cursor(mode=2)
		cursor.execute('insert into {} {} values {}'.format(tablename,
				template, values))
		conn.commit()
		#cursor.commits()

	def update_str_one(self, tablename, template, values, ident):
		cursor, conn = self.create_get_cursor(mode=2)
		cursor.execute("update {} set {}='{}' where {}".format(tablename,
			template, values, ident))
		conn.commit()

	def get_log_name(self):
		date_now = datetime.now()
		date_now = str(date_now).split('.')[0]
		date_now = date_now.replace(':','-')
		fullname = s.rfid_logs_dir2 + '/' + date_now + '.txt'
		print(fullname)
		return fullname

	def save_db_txt(self, tablename):
		log_name = self.get_log_name()
		filename = open(log_name, 'w')
		cursor = self.create_get_cursor()
		cursor.execute('select * from {}'.format(tablename))
		data = cursor.fetchall()
		for stringname in data:
			ent_date = stringname[4]
			esc_date = stringname[5]
			print('stringname is',stringname)
			here = stringname[6]
			if ent_date == None:
				ent_date = '24.08.1997 01:50'
			if esc_date == None:
				esc_date = '24.08.1997 01:50'
			ent_date = self.get_frmt_db_date(ent_date)
			esc_date = self.get_frmt_db_date(esc_date)
			if ent_date in log_name or esc_date in log_name:
				strname = str(stringname)
				strname = strname.replace('(','')
				strname = strname.replace(')','')
		filename.close()

	def get_frmt_db_date(self, date):
		date = date.split(' ')[0]
		full = date.replace('.','-')
		return full

	def update_str_two(self,tablename, values, ident1, ident2):
		cursor, conn = self.create_get_cursor(mode=2)
		cursor.execute('update {} set {} where {} and {}'.format(tablename,
			values, ident1, ident2))
		conn.commit()

	def get_last_visit(self, tablename,  ident1, ident2):
		values = self.get_all_2idents(tablename, ident1, ident2)
		listname = []
		for v in values:
			listname.append(v[8])
		for v in values:
			if v[8] == max(listname):
				return v

if __name__ == '__main__':
	sqlshell = WSQLshell('chatdb','admin','hect0r1337','localhost')
	#sqlshell.save_db_txt('ЖурналПосещений')
	ident2 = "НомерАвто='а123ам102'"
	ident1 = "НаТерритории='no'"
	#lv = sqlshell.get_last_visit('ЖурналПосещений', idenFt1, ident2)
	#lv = sqlshell.get_all_ident(s.book, ident1)
	#lv = sqlshell.get_all('Пользователи')
	sqlshell.create_str('')
	print(lv)
	#print('f')
	#sqlshell.save_db_txt('ЖурналПосещений')
