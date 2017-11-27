import socket
import time
import requests
import json

import RPi.GPIO as GPIO
from pathlib import Path


from subprocess import Popen, PIPE

BASE_URL = 'https://job-box-server.herokuapp.com/api/devices/'


def reset_email ():
	GPIO.setmode(GPIO.BOARD) #set the GPIO pins to work as numbered on the board

	reset_pin = 40 #This is the pin that is read to determine if the system needs to be reset
	high_pin = 38 #This is the pin that supplies a high signal to indicate reset
	GPIO.setup(high_pin, GPIO.OUT, initial=1) #Initial state of high_pin is high
	GPIO.setup(reset_pin, GPIO.IN, GPIO.PUD_DOWN) # reset pin is loaded with pull down

	print("the state of the reset pin is: %s (1 will clear the email registered to this device)" % GPIO.input(reset_pin)) #Check the state of the set pin

	if(GPIO.input(reset_pin)==1):
		p = Path('/home/pi/jobbox_email')
		if p.is_file():
			p.unlink()

	GPIO.cleanup()

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

	print("email uuid, url used for check/new: ", email, uuid, url)

	if email:
		r = requests.post(url, data=json.dumps({ "email": email, "uuid": uuid }), headers={ "content-type": "application/json" })
		status = r.json()
		print("check and register after hitting 'check' device route", status)

		if not status.get("success"):
			url = BASE_URL + "new"
			s = requests.post(url, data=json.dumps({ "email": email, "uuid": uuid }), headers={ "content-type": "application/json" })
			status = s.json()

			print("check and register after hitting 'new' device route", status)
			if not status.get("success"): 
				time.sleep(5)
				polling()

		else:
			pass
	else:
		print("this Pi is not associated with an email address; giving up")
		pass


def polling ():
	while not is_connected():
		time.sleep(10)

	check_and_register()
	return

reset_email()	
polling()


