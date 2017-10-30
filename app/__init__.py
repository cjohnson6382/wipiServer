
from flask import Flask, request, current_app
from flask_sqlalchemy import SQLAlchemy

from config import config

import os

db = SQLAlchemy()


def create_app(config_name):
	app = Flask(__name__)

	with app.app_context():
		app.config.from_object(config.get(config_name))
		app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

		config[config_name].init_app(app)

		@app.before_request
		def log_request():
			current_app.logger.debug(request.path)

		db.init_app(app)

		from app.main import main as main_blueprint
		app.register_blueprint(main_blueprint)

		return app