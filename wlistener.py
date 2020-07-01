import socket, logging, pickle, threading
from time import sleep
from traceback import format_exc
import wsettings as s

class WListener():
	'''Прослушиватель ком портов, к которым линкуются периферийные
	железки, при создании экземпляра необходимо задать имя железки,
	номер ком-порта, порт'''
	def __init__ (self, name='def', comnum='25', port='1488', bs = 8, py = 'N',
	sb = 1, to = 1, ip='localhost'):
		self.name = name
		self.ip = ip
		self.comnum = comnum
		self.port = port
		self.bs = bs
		self.sb = sb
		self.to = to
		self.py = py
		self.smlist = ['666']
		self.status = 'Готов'
		self.addInfo = {'carnum':'none', 'status':'none','notes':'none'}
		self.cmInterfaceComms = []
		self.activity = True
		#if s.cmUseInterfaceOn == True:
			#print('Интерфейс взаимодействия с Watchman-CM активирован')
			#threading.Thread(target=self.cmUseInterface, args=()).start()
	'''
	def wlisten(self):
		По строково читает приходящие значения и
			сохраняет последнее значение в переменную self.rval
		ser = serial.Serial(self.comnum, bytesize=self.bs,
			parity=self.py, stopbits=self.sb, timeout=self.to)
		sleep(0.5)
		self.w
data = ser.readline()
		ser.close()
		return self.data
	'''
	def wlisten_tcp(self):
		try:
			return self.smlist[-1]
		except:
			logging.error(format_exc())

	def get_value(self):
		'''Геттер для последнего прослушанного значения'''
		return self.data

	def parse_weight(self, weight):
		datal = weight.split(',')
		for el in datal:
			if 'kg' in el and len(el) > 2: pass

	def format_weight(self, weight):
		datal = weight.split(',')
		#seven = open('/home/watchman/watchman/catcher.txt','a')
		for el in datal:
			if 'kg' in el and len(el) > 2:
				el = el.replace("kg",'')
				el = el.split(' ')
				try:
					self.rcv_data = el[-2]
				except IndexError:
					###УДАЛИТЬ ПОСЛЕ ТЕСТА###
					logging.error(format_exc())
					logging.error('el is',el)
					#seven.write(str(el))
					#seven.write('\n')
					self.rcv_data = '0'
					print('incorrect weight')
					#seven.close()
				self.smlist.append(self.rcv_data)
				#print(self.rcv_data)

	def tcp_listener_server(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((s.scale_ip, s.scale_port))
		serv.listen(1997)
		while True:
			conn,addr = serv.accept()
			while True:
				while 1:
					try:

						data = conn.recv(1024)
						#print('data ', data)
						break
					except:
						sleep(1)
				if not data: break
				data = str(data)
				self.format_weight(data)
				#print('seding data to', conn)
				#for connect in self.weightRecievers:
					#connect.send(bytes(self.smlist[-1], encoding='utf-8'))
			conn.close()

	def tcp_listener_server2(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((self.ip, self.port))
		serv.listen(1997)
		while True:
			conn,addr = serv.accept()
			from_client = ''
			while True:
				while 1:
					try:
						data = conn.recv(1024)
						break
					except:
						sleep(1)
				if not data: break
				data = str(data)
				self.format_weight(data)
			conn.close()

	def statusSocket(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((s.statusSocketIp, s.statusSocketPort))
		serv.listen(1997)
		#print('c0')
		while True:
			try:
				conn,addr = serv.accept()
				while 1:
					sleep(1)
					d = pickle.dumps(self.status)
					conn.send(d)
					while self.status != 'Готов':
						sleep(1)
						x = pickle.dumps(self.addInfo)
						conn.send(x)
				conn.close()
			except:
				sleep(1)
				print('retry')

	def checkStatusChange(self, status, sleeptime=1):
		self.oldStatus = status
		sleep(sleeptime)
		self.newStatus = status
		print('OS', self.oldStatus, 'NS', self.newStatus)
		if self.newStatus != self.oldStatus:
			return True

	def cmUseInterface(self):
		serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		serv.bind((s.cmUseInterfaceIp, s.cmUseInterfacePort))
		serv.listen(1997)
		while True:
			try:
				conn,addr = serv.accept()
				while 1:
					sleep(0.5)
					comm = conn.recv(1024)
					comm = comm.decode(encoding='utf-8')
					#self.cmInterfaceComms.append(comm)
					print('Got comm from CM', comm)
					response = self.executeComm(comm)
					print('Sending response', response)
					conn.send(bytes(response, encoding='utf-8'))
					print('Comm sent')
				conn.close()
			except:
				sleep(1)
				print('cmUseInterface has been crashed. Reloading...')
				print(format_exc())

	def executeComm(self, comm):
		comm = comm.strip()
		if comm == 'freeze':
			self.status = False
			response = 'Watchman-AR freeze'
		elif comm == 'unfreeze':
			self.status = True
			response = 'Watchman-AR unfreeze'
		elif 'createStr' in comm or 'closeStr' in comm:
			self.status = False
			self.cmInterfaceComms.append(comm)
			print('Got str comm')
			response = 'comm added'
		elif 'closeRec' in comm:
			self.status = False
			self.cmInterfaceComms.append(comm)
			print('Got closeRec comm')
			response = 'comm added'
		elif 'closeLateCars' in comm:
			self.cmInterfaceComms.append(comm)
			response = 'closeLateCars command got!'
		elif comm == 'status':
			response = self.status
			print('got status request')
		else:
			print('unknown command!', comm)
			response = 'Unknown command'
		return response

	def setStatus(self, status):
		self.status = status

	def setStatusObj(self, obj):
		self.statusObj = obj

	def getStatus(self):
		return self.status

	def parseComms(self, data): pass


if __name__ == "__main__":
	scale = WListener('scale', 'COM11', 1337)
	scale.tcp_listener_server()


	#scale.tcp_listener_client()
# while 1:
		# scale.wlisten()
