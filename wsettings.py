import os

rootdir = os.getcwdb()
rootdir.decode()

# Отправка логов 18000-3605


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
