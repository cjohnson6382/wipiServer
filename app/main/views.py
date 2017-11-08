import json

from functools import wraps

from flask import request, current_app, jsonify, _app_ctx_stack
from flask_cors import cross_origin

from app import db
from app.main import main

from app.functions.functions import scan_networks, wifi_connect, clear_config, current_network, get_stored


@main.route('/get_networks', methods=["GET"])
#	@requires_auth
@cross_origin()
def networks():
	networks = scan_networks()
	print("NETWORK:", type(networks), networks)
	return jsonify(networks)

@main.route('/stored_networks', methods=["GET"])
#	@requires_auth
@cross_origin()
def stored():
	networks = get_stored()
	return jsonify(networks)

@main.route('/current_network', methods=["GET"])
#	@requires_auth
@cross_origin()
def current():
	status = current_network()
	return jsonify(status)

@main.route('/choose_network', methods=["POST"])
#	@requires_auth
@cross_origin()
def choose():
	status = wifi_connect(**request.get_json())
	return jsonify(status)

@main.route('/reset', methods=["GET"])
#	@requires_auth
@cross_origin()
def reset():
	status = clear_config()
	return jsonify(status)

@main.route('/current/<string:id>', methods=["GET"])
@cross_origin()
def current_network(id):
	current_network(id)



