from app import db
import json

import datetime

class WifiNetwork(db.Model):
	__tablename__ = 'wifi_networks'

	_created = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	_updated = db.Column(db.DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

	id = db.Column(db.Integer, primary_key=True)
	essid = db.Column(db.String(64), nullable=False)
	password = db.Column(db.String(128))

	def __init__(self, initial_data):
		for k, v in initial_data.items():
			setattr(self, k, v)

	def as_dict(self):
		try:
			dict_rep = { "essid": self.essid }
		except Exception as e:
			print('something went wrong creating a JSON file...?', e)
		return dict_rep

	def __repr__(self): return """{"type": "WifiNetwork", "id": %s, "Essid": %s, "Password": "no passar aqui" }""" % (self.id, self.essid)