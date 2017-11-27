import socket
import time
import requests
import json

from subprocess import Popen, PIPE


BASE_URL = 'https://job-box-server.herokuapp.com/api/devices/'

def is_connected ():
	try: 
		socket.create_connection(("www.google.com", 80))
		return True
	except Exception as e:
		pass

	return False

def get_serial ():
	a = Popen(args=["cat", "/proc/cpuinfo"], stdout=PIPE)
	b = Popen(args=["grep", "Serial"], stdin=a.stdout, stdout=PIPE)

	a.stdout.close()

	s = b.communicate()[0]
	serial = s.decode().split(":")[1].strip()

	return serial

def get_email ():
	with open("/home/pi/jobbox_email", "r+") as f:
		email = f.read()

		if email: return email
		else: return False

def check_and_register ():
	url = BASE_URL + "check"

	email = get_email()
	uuid = get_serial()

	if email:
		r = requests.post(url, data=json.dumps({ "email": email, "uuid": uuid }), headers={ "accept": "application/json" })
		status = r.json()
		print("check and register after hitting 'check' device route", status)

		if not status.get("success"):
			url = BASE_URL + "new"
			s = requests.post(url, data=json.dumps({ "email": email, "uuid": uuid }), headers={ "accept": "application/json" })
			status = s.json()
			
			print("check and register after hitting 'new' device route", status)
			if not status.get("success"): 
				time.sleep(5)
				polling()
	else:
		print("this Pi is not associated with an email address; giving up")
		pass


def polling ():
	while not is_connected():
		time.sleep(10)

	check_and_register()
	return
		
polling()