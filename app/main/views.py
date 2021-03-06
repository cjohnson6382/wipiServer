import json

from functools import wraps

from flask import request, current_app, jsonify, _app_ctx_stack, render_template
from flask_cors import cross_origin

from app import db
from app.main import main

from app.functions.functions import scan_networks, wifi_connect, clear_config, current_network, get_stored, disconnect, wifi_add, get_serial, email_address, register

@main.route('/', methods=["GET"])
@cross_origin()
def root():
	return render_template('index.html')

@main.route('/static/<string:route>', methods=["GET"])
@cross_origin()
def bundle(route):
	return url_for("static", filename=route)


@main.route('/register', methods=["POST"])
@cross_origin()
def register_email():
	status = register(**request.get_json())
	return jsonify(status)

@main.route('/email_address', methods=["GET"])
@cross_origin()
def email():
	email = email_address()

	print("Views email_address returned, should be a string not a bool: ", email)

	return jsonify(email)

@main.route('/serial_number', methods=["GET"])
@cross_origin()
def serial():
	serial = get_serial()

	print(serial)

	return jsonify(serial)

@main.route('/get_networks', methods=["GET"])
#	@requires_auth
@cross_origin()
def networks():
	networks = scan_networks()

	print('NETWORKS', networks)

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

	print(status)

	return jsonify(status)

@main.route('/choose_network', methods=["POST"])
#	@requires_auth
@cross_origin()
def choose():
	status = wifi_connect(**request.get_json())
	return jsonify(status)

@main.route('/save_network', methods=["POST"])
#	@requires_auth
@cross_origin()
def save():
	status = wifi_add(**request.get_json())
	return jsonify(status)

@main.route('/reset', methods=["GET"])
#	@requires_auth
@cross_origin()
def reset():
	status = clear_config()
	return jsonify(status)

@main.route('/disconnect', methods=["GET"])
@cross_origin()
def disconnect_wifi():
	status = disconnect()
	return jsonify(status)

# @main.route('/current/<string:id>', methods=["GET"])
# @cross_origin()
# def current_network(id):
# 	current_network(id)