from wlistener import WListener
import socket, threading, pickle, os
import wsettings as s


class WChatServer(WListener):
	def __init__(self,name='def', comnum='25', port='1488', bs = 8, py = 'N',
		sb = 1, to = 1, ip='localhost', sqlshell='none'):
		WListener.__init__(self, name, comnum, port, bs, py, sb, to, ip)
		# Словарь где будет инфа, кто сколько отправил непрочитанных сообщений
		self.sentNotReadMsgs = {}
		rootdir = os.getcwd()
		self.statusFile = rootdir + '/wstat.cfg'
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
			command = data.decode()
			if len(command) > 1:
				print('Основное тело цикла сервер АПИ')
				if command == 'getChat':
					conn.send(b"trash")
					print('getChat got', command)
					self.chatInterface(conn)
				elif command == 'getStatus':
					print('getStatus got', command)
					status = pickle.dumps(self.sentNotReadMsgs)
					conn.send(status)
				else:
					print('got unidentified command', command)

	def chatInterface(self, conn):
		'''Сервер обмена сообщениями
		1. Клиент подключается, указав свой логин
		2. Сервер ждет id чата
		3. Получив id отправляет ему id чата'''
		while True:
			print('Есть подключение к серверу сообщений. Ждем логин')
			data = conn.recv(1024)
			data = data.decode()
			requester = data
			usrIdSpl = ';'
			endMsgSpl = '  END&MSG  '
			endFrSpl = '  FRAG&END  '
			metaDataSpl = '  META&DATA  '
			requester = data.split(usrIdSpl)[0]
			chatid = data.split(usrIdSpl)[1]
			print('\nrequester -', requester)
			#print('chatid -', chatid)
			print('chatid -', chatid)
			totalMsgs = self.getTotalMsgs(chatid)
			logfilepath = '/home/watchman/chatServer/chatlogs/log_{}id.txt'.format(chatid)
			try:
				logfile = open(logfilepath, 'r')
				chatdata = logfile.read()
				chatdata = chatdata.split(endMsgSpl)
				newmsgs = []
				for msg in chatdata:
					#print('data from new func', data)
					data = msg.split(endFrSpl)
					print('msg is', msg)
					print('data is', data)
					if len(data) > 2:
						print('data from new func', data)
						new_data = self.dicremCount(data, chatid, requester)
						new_msg = endFrSpl.join(data)
						print('new msg - ', new_msg)
						newmsgs.append(new_msg)
				self.saveStatus()
				newlog = endMsgSpl.join(newmsgs)
				print('newlog is', newlog)
				chatdata = pickle.dumps(newlog)
				conn.send(chatdata)
				logfile.close()

				# Сохранение нового лога
				logfile = open(logfilepath, 'w')
				logfile.write(newlog)
				logfile.close()
				#chatdata =
					#msgStatus = data[1]
					#if msgStatus == 'NOT READ:
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
				msg = endMsgSpl + data['username'] + endFrSpl
				msg += data['data'] + endFrSpl + data['time']
				msg += endFrSpl + 'NOT READ'
				self.incremCount(data, chatid, totalMsgs)
				logfile.write(msg)
				logfile.close()
			conn.close()

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
