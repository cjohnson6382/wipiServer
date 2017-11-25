import os

if os.path.exists('.env'):
		print('Importing environment from .env...')
		for line in open('.env'):
				var = line.strip().split('=')
				if len(var) == 2:
						os.environ[var[0]] = var[1]

from flask_script import Manager, Shell, Server
from flask_migrate import Migrate, MigrateCommand

from flask_sqlalchemy import SQLAlchemy

from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db)
manager = Manager(app)

if os.environ.get('APP_SETTINGS') == 'config.HerokuConfig':
	manager.add_command('runserver', Server(host='0.0.0.0', port=os.environ.get("PORT", 5000), threaded=True))

manager.add_command('db', MigrateCommand)

@manager.command
def deploy():
		"""Run deployment tasks."""
		from flask_migrate import upgrade


		# migrate database to latest revision
		upgrade()

if __name__ == '__main__':
		manager.run()