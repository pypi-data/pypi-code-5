#!/usr/bin/python


import re, time, sys
try:
	from urllib.request import urlopen
except:
	from urllib import urlopen
sys.path.insert(0, '/etc/storemyip')
from config import *


def ask_ip():
	global ip
	# Search of IPv4
	ip_n = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', str(urlopen(server).read()))[0]
	try:
		ip
	except:
		ip = ip_n
		print('Your ip is ' + ip)
		return True
	if ip != ip_n:
		ip = ip_n
		print('Your new ip is ' + ip)
		return True
	return False


def write_ip():
	global ip
	file_ip = open(file_name, 'w')
	file_ip.write(ip)


print('\n')


while True:
	new_ip = ask_ip()
	if new_ip:
		if writing_in_file:
			print('Writing in file...')
			write_ip()
	time.sleep(update_time)