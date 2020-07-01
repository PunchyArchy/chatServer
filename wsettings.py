import os

rootdir = os.getcwdb()
rootdir.decode()

# Отправка логов 18000-3605
logs_send_rate = 18000
logs_check_rate = 3605
rfid_logs_dir = '/home/watchman/watchman/rfid_logs'
rfid_logs_dir2 = rfid_logs_dir
scale_lis_time = 5
scale_est_time = 3
diff_value = 2000
auto = 'Авто'
book = 'ЖурналПосещений'
twt = 0
twtesc = 0
after_wait_time = 7

#ДБ PostgreSQL
db_name = 'wdb'
db_user = 'watchman'
db_pass = 'hect0r1337'
db_location = '192.168.100.109'

#Параметры для wcheker`a
ad_pc_this = 0.4
ad_pc_model = 0.5
ad_pc_all = 0.8
ad_ret_time = 7200
ad_in_time = 3600
ignore_deviations = True

# Время
ad_re_time = 7200
ad_pr_time = 3600

#Настройки контроллера СКУД
contr_ip = 'localhost'
contr_port = 3312
entry_gate_num = '2'
entry_ph_num = '3'
exit_gate_num = '1'
exit_ph_num = '4'
ph_lock_state = '31'
ph_unlock_state = '30'

#FTP settings
ftp_ip = '192.168.100.111'
ftp_login = 'watchman'
ftp_pw = 'OTENTaRtiCEA'

#Настройки TCP прослушивателя весов
scale_ip = '192.168.100.186'
scale_port = 2290

#Настройка сокета для передачи статуса  Watchman-CM
statusSocketIp = '192.168.100.109'
statusSocketPort = 2291

#Настройки камеры
cam_login = 'admin'
cam_pw = 'hect0r1337'
cam_com = 'http://{}-{}@192.168.100.139/ISAPI/Streaming/channels/101/picture?snapShotImageType=JPEG'.format(cam_login, cam_pw)
pics_folder = '/home/watchman/watchman/pics/'
count_file = '/home/watchman/watchman/cam_count.cfg'
fpath_file = '/home/watchman/watchman/fpath.cfg'

#Настройка реакции на фотоэлементы
ph_time = 6
ad_weight_rfid = 500
lib_time = 4
ph_release_timer = 120

#RFIDE RESUB
rfid_resub = 120

#Механизм ожидания выравнивания перед фотоэлементами
max_wait = 60
min_weight = -10

diffRepEx = 2700

#Настройки сокета для получения комманд от Watchman-CM
cmUseInterfaceOn = True
cmUseInterfaceIp = '192.168.100.109'
cmUseInterfacePort = 2292
