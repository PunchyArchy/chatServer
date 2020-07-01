from wlistener import WListener
import socket, threading, pickle, os
import wchat_config as cfg
from wsqluse import WSQLshell


class WChatServer(WListener):
	def __init__(self,name='def', comnum='25', port='1488', bs = 8, py = 'N',
		sb = 1, to = 1, ip='localhost'):
		WListener.__init__(self, name, comnum, port, bs, py, sb, to, ip)
		# Словарь где будет инфа, кто сколько отправил непрочитанных сообщений
		self.sentNotReadMsgs = {}
		rootdir = os.getcwd()
		self.statusFile = rootdir + '/wstat.cfg'
		# подключение к БД
		self.sqlshell = WSQLshell(cfg.dbName, cfg.dbUser, cfg.dbPw, cfg.dbIp)
		try:
			self.getStatus()
		except:
			self.saveStatus()
		self.sqlshell = sqlshell

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

	def dispatcher(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((self.ip, self.port))
		serv.listen(1024)
		while True:
			print('\n\nСервер сообщений запущен.')
			conn, addr = serv.accept()
			print('Есть клиент')
			threading.Thread(target=self.serverApi, args=(conn,)).start()

	def serverApi(self, conn):
		while True:
			data = conn.recv(1024)
			comm = picke.loads(data)
			print('command', comm)
			for command in list(comm.keys()):
				print('Основное тело цикла сервер АПИ')
				if command == 'getChat':
					#conn.send(b"trash")
					#print('getChat got', command)
					self.chatInterface(conn)
				elif command == 'sendMsg':
					print('sendMsg got', command)
					self.createNewMsg(comm.values())
					#UPDATE RECIEVER!
				else:
					print('got unidentified command', command)

	def createNewMsg(self, msgs):
		'''Парсер новых сообщений. Получает новое сообщение и парсит его'''
		for msg in list(msgs):
			template = ('sender', 'destination', 'message', 'date', 'ifread')
			values = ("'{}'","'{}'","'{}'", date, 'false')
			values = values.format(msg['sender'], msg['destination'],
				msg['message'])
			self.sqlsehll.сreate_str(self, cfg.msgTable, template, values)

	def getSortedMsgs(self, allMsgs):
		allMsgs.sort(key=self.takeDate)
		return allMsgs

	def takeDate(self, msg):
		return msg[1]

	def getOldParseMsgs(self, allMsgs):
		newlog = ''
		for msg in allMsgs:
			if msg[4] == 'f':
				ifRead = 'Not Read'
			else:
				ifRead = 'READ'
			newlog += msg[0] + cfg.endFrSpl + msg[2] + cfg.endFrSpl + msg[3]
			newlog += cfg.endFrSpl + ifRead + cfg.endMsgSpl
		return newlog

	def chatInterface(self, conn):
		'''Сервер обмена сообщениями
		1. Клиент подключается, указав свой логин
		2. Сервер ждет комманду
		3.1 Получив id отправляет ему id чата
		3.2 Получив изменение высылает ему изменения'''
		while True:
			print('Есть подключение к серверу сообщений. Ждем логин')
			data = conn.recv(1024)
			data = data.decode()
			requester = data.split(cfg.usrIdSpl)[0]
			chatid = data.split(cfg.usrIdSpl)[1]
			print('\nrequester -', requester)
			print('chatid -', chatid)
		#	totalMsgs = self.getTotalMsgs(chatid)
			#logfilepath = '/home/watchman/chatServer/chatlogs/log_{}id.txt'.format(chatid)
			ident = "chatId = '{}'".format(chatid)
			spec = 'sender, destination, message, date'
			allMsgs = self.sqlshel.get_special_ident(cfg.msgTable, spec, ident)
			allMsgs = self.getSortedMsgs()
			# OLD PARSING EMULATING
			newlog = self.getOldParseMsgs(allMsgs)
			chatdata = pickle.dumps(newlog)
			conn.send(chatdata)
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
