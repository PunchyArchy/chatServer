from wchatServer import WChatServer
import threading, os,sys
sys.path.append('/home/watchman/.local/lib/python3.8/site-packages')
print(sys.path)
from wsqluse import WSQLshell
import wchat_config as cfg

tcpServer = WChatServer(port=cfg.port, ip=cfg.ip)
#print(wc.ip,wc.port)
try:
	threading.Thread(target=tcpServer.tcpLoggingServ, args=()).start()
except KeyboardInterrupt:
	os._exit()
