import os
basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
	#	used by Flask
	SECRET_KEY = os.environ.get('SECRET_KEY') or 'an unbelievably hard to guess string that has numbers 1235984 and symbols @#%*!&'
	SERVER_PREFIX = os.environ.get('SERVER_PREFIX')
	SERVER_NAME = os.environ.get('SERVER_NAME')
	#	all of the auth routes use id/secret to get an access_token from auth0
	# AUTH0_CLIENT_ID = os.environ.get('AUTH0_CLIENT_ID')
	# AUTH0_CLIENT_SECRET = os.environ.get('AUTH0_CLIENT_SECRET')

	FLASK_CONFIG = os.environ.get("FLASK_CONFIG")

	#	this is the address of the running server; should change based on the config we use, not the contents of .env
	SERVER = os.environ.get('SERVER')
	SSL_DISABLE = False
	SQLALCHEMY_COMMIT_ON_TEARDOWN = True
	SQLALCHEMY_RECORD_QUERIES = True

	#	SQLALCHEMY_TRACK_MODIFICATIONS=True
	AUTH0_URL = os.environ.get('AUTH0_URL')

	@staticmethod
	def init_app(app):
			pass


class DevelopmentConfig(Config):
	DEBUG = True
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
			'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


#	 need to customize this for our testing environment
class TestingConfig(Config):
	TESTING = True

	SQLALCHEMY_DATABASE_URI = os.environ.get('TEST_DATABASE_URL')

	WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
	SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
			'sqlite:///' + os.path.join(basedir, 'data.sqlite')

	@classmethod
	def init_app(cls, app):
			Config.init_app(app)



class HerokuConfig(ProductionConfig):
	SSL_DISABLE = bool(os.environ.get('SSL_DISABLE'))
	SERVER_PREFIX = os.environ.get('HOSTNAME')
	@classmethod
	def init_app(cls, app):
			ProductionConfig.init_app(app)

			# handle proxy server headers
			from werkzeug.contrib.fixers import ProxyFix
			app.wsgi_app = ProxyFix(app.wsgi_app)

			# log to stderr
			import logging
			from logging import StreamHandler
			file_handler = StreamHandler()
			file_handler.setLevel(logging.WARNING)
			app.logger.addHandler(file_handler)


class UnixConfig(ProductionConfig):
	@classmethod
	def init_app(cls, app):
			ProductionConfig.init_app(app)

			# log to syslog
			import logging
			from logging.handlers import SysLogHandler
			syslog_handler = SysLogHandler()
			syslog_handler.setLevel(logging.WARNING)
			app.logger.addHandler(syslog_handler)


config = {
	'development': DevelopmentConfig,
	'testing': TestingConfig,
	'production': ProductionConfig,
	'heroku': HerokuConfig,
	'unix': UnixConfig,

	'default': DevelopmentConfig
}
