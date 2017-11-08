import functools

from subprocess import run
from subprocess import PIPE

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
def get_stored ():
	r = WifiNetwork.query.all()
	stored = [w.as_dict() for a in r]
	return stored

def wifi_add (essid, password):
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
	a = run(args=["sudo", "/sbin/wpa_supplicant", "-i wlan1", "-c ./wpa_supplicant.conf", "-B"], stdout=PIPE)
	b = a.stdout.decode()
	if "Successfully initialized wpa_supplicant" in b: return True
	else: return False

def wifi_connect (essid="", password=""):
	# 	this will have to be expanded to account for different authentication scenarios
	if essid:
		w = WifiNetwork.query.filter(WifiNetwork.essid == essid).first()
		if w:
			if write_conf(w.essid, w.password):
				connect()
			if not r: return { "status": "failed to set wpa_supplicant.conf to %s" % w.essid }
			if connect(): pass
			else: return { "status": "failed to connect to %s" % w.essid }
		else: 
			if not password: return { "status": "cannot connect to %s; not saved and no password supplied" % essid }
			if wifi_add(essid, password):
				write_conf(essid, password)
				if connect(): pass
				else: return { "status": "failed to connect to %s" % essid }
			else: return { "status": "failed to add wifi network to wpa_supplicant conf" }
		
		return { "status": "connected to %s" % essid }
	else: return { "status": "no ESSID provided; what network should I connect to?" }

def disconnect ():
	a = run(args=["sudo", "/usr/bin/killall", "wpa_supplicant"], stdout=PIPE)
	b = run(args=["sudo", "/sbin/iw", "dev", "wlan1", "link"], stdout=PIPE)
	c = b.stdout.decode()
	if "Not connected." in c:
		return True

def clear_config ():
	c = disconnect()

	ww = WifiNetwork.query.all()
	[db.session.delete(w) for w in ww]
	db.session.commit()

	if c:
		return { "status": "deleted all stored wifi networks" }
	else: 
		return { "status": "" }

def current_network ():
	a = run(args=["sudo", "/sbin/iw", "wlan1", "link"], stdout=PIPE)
	b = a.stdout.decode()
	c = b.split("\n")
	d = [a.split(":", 1) for a in c]
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
	print(essid)
	if essid:
		essid = essid.strip('"')
		cell.setlist("ESSID", [essid])		
	return cell

# def strip_elements (cell):
# 	c = [a.strip() for a in cell]
# 	print(type(cell))
# 	return c

convert_pipeline = compose([fix_ie, fix_essid, dictify])

def scan_networks ():
	a = run(args=["sudo", "/sbin/iwlist", "wlan1", "scanning"], stdout=PIPE)
	b = a.stdout.decode()

	c = b.split("Cell")
	d = [a.split("\n") for a in c]

	networks = [convert_pipeline(a) for a in d]
	networks = [a.to_dict() for a in networks]
	print(networks)
	return networks
