from wchatServer import WChatServer
import threading, os,sys
sys.path.append('/home/watchman/.local/lib/python3.8/site-packages')
print(sys.path)
from wsqluse import WSQLshell
import wsettings as s
import wchat_config as wc

sqlshell = WSQLshell(s.db_name, s.db_user, s.db_pass, s.db_location)
tcpServer = WChatServer(port=wc.port, ip=wc.ip,sqlshell=sqlshell)
print(wc.ip,wc.port)
try:
	threading.Thread(target=tcpServer.tcpLoggingServ, args=()).start()
except KeyboardInterrupt:
	os._exit()
