from wlistener import WListener
import socket, threading, pickle, os
import wchat_config as cfg
from wsqluse import WSQLshell
from datetime import datetime
from time import sleep

class WChatServer(WListener):
	def __init__(self,name='def', comnum='25', port='1488', bs = 8, py = 'N',
		sb = 1, to = 1, ip='localhost'):
		WListener.__init__(self, name, comnum, port, bs, py, sb, to, ip)
		# Словарь где будет инфа, кто сколько отправил непрочитанных сообщений
		self.sentNotReadMsgs = {}
		rootdir = os.getcwd()
		self.date_pattern = '%d.%m.%y %H:%M:%S'
		self.statusFile = rootdir + '/wstat.cfg'
		self.connectedUsrs = {}
		self.shownMessages = {}
		#self.shownMessages = []
		self.ifUpdate = {}
		# подключение к БД
		self.sqlshell = WSQLshell(cfg.dbName, cfg.dbUser, cfg.dbPw, cfg.dbIp)
		try:
			self.getStatus()
		except:
			self.saveStatus()
		#self.sqlshell = sqlshell

	def tryGetUsr(self, usr, chatid):
		try:
			data = self.sentNotReadMsgs[usr]
		except KeyError:
			self.sentNotReadMsgs[usr] = {chatid:0}
			data = self.sentNotReadMsgs[usr]
		return data

	def incremCount(self, data, chatid, totalMsgs):
		usr = data['username']
		usrdata = self.tryGetUsr(usr, chatid)
		self.tryIncrem(usr, usrdata, chatid)
		msg = 'Сообщение отправлено'
		msg += 'Всего у {} {} непрочитанных сообщений'.format(usr,
			str(self.getAllMsgs(usr)))
		self.saveStatus()
		self.incremDbCount(chatid, totalMsgs)
		print(msg)

	def saveStatus(self):
		fobj = open(self.statusFile, 'wb')
		data = pickle.dumps(self.sentNotReadMsgs)
		fobj.write(data)
		fobj.close()

	def getStatus(self):
		fobj = open(self.statusFile, 'rb')
		data = pickle.loads(fobj.read())
		print('got data from status file', data)
		self.sentNotReadMsgs = data
		fobj.read()

	def tryIncrem(self, usr, usrdata, chatid):
		try:
			self.sentNotReadMsgs[usr][chatid] += 1
		except KeyError:
			self.sentNotReadMsgs[usr][chatid] = 1

	def dicremCount(self, data, chatid, requester):
		usr = data[0]
		status = data[3]
		try:
			if requester != usr and status != 'READ':
				data[3] = 'READ'
				self.sentNotReadMsgs[usr][chatid] -= 1
				msg = 'Сообщение прочтено. Непрочитанный сообщений от {} осталось {} штук'.format(usr, str(self.getAllMsgs(usr)))
				print(msg)
		except KeyError:
			if requester != usr and status != 'READ':
				self.sentNotReadMsgs[usr][chatid] = 0
		return data

	def getAllMsgs(self, usr):
		'''Читает количество непрочитанных сообщений'''
		usrdata = self.sentNotReadMsgs[usr]
		count = 0
		for k,v in usrdata.items():
			count += 1
		return count

	def tcpLoggingServ(self):
		self.dispatcher()
		#self.updDispatcher()

	def dispatcher(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((self.ip, self.port))
		serv.listen(1024)
		while True:
			print('\n\nСервер сообщений запущен.')
			conn, addr = serv.accept()
			print('Есть клиент')
			#self.shownMessages = []
			threading.Thread(target=self.serverApi, args=(conn,)).start()

	def updDispatcher(self):
		serv = socket.socket()
		serv.bind((self.ip, cfg.updPort))
		serv.listen(1024)
		while True:
			print('\nСервер отправки обновлений запущен.')
			conn, addr = serv.accept()
			print('Есть клиент')
			self.shownMessages[conn] = []
			threading.Thread(target=self.updSender, args=(conn,)).start()

	def getData(self,conn):
		print('Получение данных')
		data = conn.recv(1024)
		#print('data ', data)
		if len(data) > 0:
			data = pickle.loads(data)
			print('Данные получены', data)
			return data
	
	def sendData(self, conn, data):
		print('Отправка данных', data)
		data = pickle.dumps(data)
		conn.send(data)
		print('Данные отправлены')

	def serverApi(self, conn):
		#print('Ждем логин')
		#username = self.getData(conn)
		#self.connectedUsrs[username] = conn
		while True:
			#self.shownMessages= []
			print('Ждем комманду от клиента')
			comm = self.getData(conn)
			print('command', comm)
			if not comm: break
			if type(comm) == dict:
				for command, info in comm.items():
					print('Основное тело цикла сервер АПИ')
					if command == 'getChat':
						self.chatInterface(conn, info)
					elif command == 'sendMsg':
						print('sendMsg got', command)
						self.createNewMsg(info)
						#UPDATE RECIEVER!
					#elif command == 'getUpd':
						#self.sendUpd(conn, info)
					else:
						print('got unidentified command', command)

	def updSender(self, conn):
		upd = {}
		#username = info['username']
		while True:
			data = self.getData(conn)
			if not data: break
			info = list(data.values())[0]
			username = info['username']
			#chatid = info['chatId']
			ident = "destination='{}'".format(username)
			ident2 = "ifread=False"
			print('Получаем все непрочитанные сообщения пользователя')
			allunreadmsgs = self.sqlshell.get_all_2idents(cfg.msgTable, ident, ident2)
			print('allunread', allunreadmsgs)
			notShownMsgs = list(set(allunreadmsgs) - set(self.shownMessages[conn]))
			upd['unreadMsgs'] = notShownMsgs
			#while True:
			#if len(upd['unreadMsgs']) > 0:
			self.sendData(conn, upd)
			for msg in allunreadmsgs:
				self.shownMessages[conn].append(msg)
			#	break
				#else: 
				#	sleep(1)
				#	print('Нет обновлений для отправки')
				#	try: self.sendData(conn, upd)
				#	except: 
				#		print('Клиент отключился')
				#		break
		#	break
					#print(dir(conn))
					#data = self.getData(conn)
					#newusr = list(data.values())[0]['username']
					#if newusr != username:
						#break
			#self.ifUpdate[username] = False
		#else:
			#self.sendData(conn, 'noUpd')

	def getTimeNow(self):
		now = datetime.now()
		now = now.strftime(self.date_pattern)
		return now

	def createNewMsg(self, msg):
		'''Парсер новых сообщений. Получает новое сообщение и парсит его'''
		date = self.getTimeNow()
		template = '(sender, destination, message, date, ifread, chatid)'
		values = "('{}','{}','{}', '{}', 'false', '{}')"
		values = values.format(msg['username'], msg['destination'],
			msg['data'], date, msg['chatid'])
		self.sqlshell.create_str(cfg.msgTable, template, values)
		self.ifUpdate[msg['destination']] = True

	def getSortedMsgs(self, allMsgs):
		allMsgs.sort(key=self.takeDate)
		return allMsgs

	def takeDate(self, msg):
		return msg[3]

	def getOldParseMsgs(self, allMsgs):
		newlog = ''
		print('allMsgs', allMsgs)
		for msg in allMsgs:
			#print('msg',msg)
			if msg[4] == 'f':
				ifRead = 'Not Read'
			else:
				ifRead = 'READ'
			date = datetime.strftime(msg[3], self.date_pattern)
			newlog += msg[0] + cfg.endFrSpl + msg[2] + cfg.endFrSpl + date
			newlog += cfg.endFrSpl + ifRead + cfg.endMsgSpl
		return newlog

	def chatInterface(self, conn, info):
		#requester = info['login']
		chatid = info['chatid']
		#print('\nrequester -', requester)
		print('chatid -', chatid)
		#	totalMsgs = self.getTotalMsgs(chatid)
			#logfilepath = '/home/watchman/chatServer/chatlogs/log_{}id.txt'.format(chatid)
		ident = "chatId = '{}'".format(chatid)
		spec = 'sender, destination, message, date, ifread, msgid'
		allMsgs = self.sqlshell.get_special_ident(cfg.msgTable, spec, ident)
		print('allmsgs - ', allMsgs)
		if len(allMsgs) > 0:
			allMsgs = self.getSortedMsgs(allMsgs)
			print('sorted allMsgs', allMsgs)
			# OLD PARSING EMULATING
			newlog = self.getOldParseMsgs(allMsgs)
			print('new log is', newlog)
			readMsgs = []
			for msg in allMsgs:
				#print('msg -',msg)
				if msg[0] != info['login'] and msg[4] == False:
					readMsgs.append(msg[5])
			ident1 = ''
			for msg in readMsgs:
				if len(ident1) > 0:
					ident1 += 'or msgid={}'.format(msg)
				else:
					ident1 += 'msgid={}'.format(msg)
			# Determine if there are not read msgs for user
			if len(readMsgs) > 0:
				self.sqlshell.update_str_one(cfg.msgTable, 'ifread','true',ident1)
			print('newlog', newlog)
		else: 
			print('sending no log')
			newlog = b''
		chatdata = pickle.dumps(newlog)
		conn.send(chatdata)
		print('chatdata was sent')
		'''
			try:
				logfile = open(logfilepath, 'r')
				chatdata = logfile.read()
				chatdata = chatdata.split(cfg.endMsgSpl)
				newmsgs = []
				for msg in chatdata:
					#print('data from new func', data)
					data = msg.split(cfg.endFrSpl)
					print('msg is', msg)
					print('data is', data)
					if len(data) > 2:
						print('data from new func', data)
						new_data = self.dicremCount(data, chatid, requester)
						new_msg = cfg.endFrSpl.join(data)
						print('new msg - ', new_msg)
						newmsgs.append(new_msg)
				self.saveStatus()
				newlog = cfg.endMsgSpl.join(newmsgs)
				print('newlog is', newlog)
				chatdata = pickle.dumps(newlog)
				conn.send(chatdata)
				logfile.close()

				# Сохранение нового лога
				logfile = open(logfilepath, 'w')
				logfile.write(newlog)
				logfile.close()
			except FileNotFoundError:
				chatdata = b''
				chatdata = pickle.dumps(chatdata)
				conn.send(chatdata)
			while 1:
				logfile = open(logfilepath,'a')
				print('Ожидаются данные для логирования')
				data = conn.recv(1024)
				if not data:
					print('Нет данных')
					break
				print('Есть сообщение!', data)
				conn.send(data)
				data = pickle.loads(data)
				msg = cfg.endMsgSpl + data['username'] + cfg.endFrSpl
				msg += data['data'] + cfg.endFrSpl + data['time']
				msg += cfg.endFrSpl + 'NOT READ'
				self.incremCount(data, chatid, totalMsgs)
				logfile.write(msg)
				logfile.close()
			conn.close()
		'''

	def incremDbCount(self, chatid, totalMsgs):
		'''Увеличивает totalMsgs в базе данных'''
	#	totalMsgs = self.getTotalMsgs(chatid)
		ident = "chatid='{}'".format(chatid)
		totalMsgs += 1
		self.sqlshell.update_str_one('chatinfo', 'totalmsgs', totalMsgs,ident)

	def getTotalMsgs(self, chatid):
		ident = "chatid='{}'".format(chatid)
		rec = self.sqlshell.get_all_ident('chatinfo', ident)
		print(rec)
		try:
			total = rec[0][3]
		except: total = 0
		print(total)
		return total
