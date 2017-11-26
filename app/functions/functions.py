import functools

from app import db

from subprocess import run, Popen, PIPE

from app.models import WifiNetwork

from werkzeug.datastructures import MultiDict

def compose(functions):
	if (len(functions) > 1):
		return functools.reduce(lambda f, g: lambda x: f(g(x)), functions, lambda x: x)
	else:
		return functions[0]


# https://wiki.archlinux.org/index.php/WPA_supplicant
# https://wireless.wiki.kernel.org/en/users/documentation/iw
# https://wiki.archlinux.org/index.php/WPA_supplicant#Connecting_with_wpa_cli

########################################################

def email_address ():
	with open("/home/pi/jobbox_email", "a+") as f:
		email = f.read()

		if email: return email
		else: return False

def register (uuid, email=""):
	print("register, args:", uuid, email)

	if email:
		f = open("/home/pi/jobbox_email", "w")
		f.write(email)
		f.close()
	else:
		f = open("/home/pi/jobbox_email", "w")
		email = f.read()
		f.close()

	if len(len(email) > 2):
		r = requests.post(url, data=json.dumps({ "email": email, "uuid": uuid }), headers={ "accept": "application/json" })
		return r.get("success")
	else:
		print("no email address provided and no saved email exists")
		return False




def get_serial ():
	a = Popen(args=["cat", "/proc/cpuinfo"], stdout=PIPE)
	b = Popen(args=["grep", "Serial"], stdin=a.stdout, stdout=PIPE)

	a.stdout.close()

	s = b.communicate()[0]
	serial = s.decode().split(":")[1].strip()

	return serial


def get_stored ():
	r = WifiNetwork.query.all()

	stored = [w.as_dict() for w in r]

	print(stored)

	return stored

def wifi_add (essid, password=""):

	print("ESSID, PASSWORD in wifi_add: ", essid, password)

	w = WifiNetwork.query.get(essid)	
	if w and password: 
		print("network exists, changing password from %s to %s" % (w.password, password))
		w.password = password
		return True
	else:
		print("network does not exist, saving network %s" % essid)
		w = WifiNetwork({ "essid": essid, "password": password })
		db.session.add(w)
		db.session.commit()
		return True

def write_conf (essid, password):
	a = run(args=["sudo", "/usr/bin/wpa_passphrase", essid, password], stdout=PIPE)
	b = a.stdout.decode()

	f = open("./wpa_supplicant.conf", 'w')
	f.write(b)
	f.close()

	return True

def connect ():
	a = run(args=["sudo", "/sbin/wpa_supplicant", "-iwlan1", "-cwpa_supplicant.conf", "-B"], stdout=PIPE)

	print(a)

	b = a.stdout.decode()

	if "Successfully initialized wpa_supplicant" in b: return True
	else: return False

def get_network (essid):
	a = run(args=["sudo", "iw", "link", "set", "wlan1", "up"], stdout=PIPE)


def wifi_connect (essid="", password=""):
	disconnect()
	a = run(args=["sudo", "ip", "link", "set", "wlan1", "up"], stdout=PIPE)
	# 	this will have to be expanded to account for different authentication scenarios
	if essid:
		w = WifiNetwork.query.get(essid)
		if w:
			r = False
			if write_conf(w.essid, w.password):
				if connect(): return { "status": "connected to %s" % w.essid}
				else: return { "status": "failed to connect to %s" % w.essid }
			else: return { "status": "failed to set wpa_supplicant.conf to %s" % w.essid }
		else: 
			# if not password: return { "status": "cannot connect to %s; not saved and no password supplied" % essid }
			if wifi_add(essid, password):
				write_conf(essid, password)
				if connect(): return { "status": "connected to %s" % essid}
				else: return { "status": "failed to connect to %s" % essid }
			else: return { "status": "failed to add wifi network to wpa_supplicant conf" }

	else: return { "status": "no ESSID provided; what network should I connect to?" }

def disconnect ():
	print("running disconnect")
	a = run(args=["sudo", "/usr/bin/pkill", "wpa_supplicant"], stdout=PIPE)
	b = run(args=["sudo", "ip", "link", "set", "wlan1", "down"], stdout=PIPE)

	c = run(args=["sudo", "/sbin/iw", "dev", "wlan1", "link"], stdout=PIPE)
	d = c.stdout.decode()
	if "Not connected." in d:
		return True
	else: return False

def clear_config ():
	c = disconnect()

	ww = WifiNetwork.query.all()
	[db.session.delete(w) for w in ww]
	db.session.commit()

	if c:
		return { "status": "disconnected and deleted all stored wifi networks" }
	else: 
		return { "status": "I do not even know; you suck at this" }

def current_network ():
	print("in current_network function")
	a = run(args=["sudo", "/sbin/iwconfig", "wlan1"], stdout=PIPE)
	b = a.stdout.decode()
	c = b.split("\n")

	print("CURRENT NETWORK FUNCTION: ", c)

	d = [a.split(":", 1) for a in c]

	print(d)

	e = [a for a in d if len(a) > 1]



	network = dict([(a[0].strip(), a[1].strip()) for a in e])

	return network

########################################################

def dictify (l):
	t = [a.strip() for a in l]
	t1 = [a.split(":", 1) for a in t]
	t2 = MultiDict([a for a in t1 if len(a) > 1])
	return t2

def fix_ie (cell):
	cell.setlist("IE", list(filter(lambda x: "Unknown" not in x, cell.getlist("IE"))))
	return cell

def fix_essid (cell):
	essid = cell.get("ESSID")
	if essid:
		essid = essid.strip('"')
		cell.setlist("ESSID", [essid])		
	return cell

convert_pipeline = compose([fix_ie, fix_essid, dictify])

def scan_networks ():
	a = run(args=["sudo", "ip", "link", "set", "wlan1", "up"], stdout=PIPE)
	b = run(args=["sudo", "/sbin/iwlist", "wlan1", "scanning"], stdout=PIPE)
	c = b.stdout.decode()

	d = c.split("Cell")
	e = [a.split("\n") for a in d]

	e.pop(0)

	networks = [convert_pipeline(a) for a in e]
	networks = [a.to_dict(flat=False) for a in networks]

	return networks
