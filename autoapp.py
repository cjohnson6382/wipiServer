#	gunicorn does not route my requests correctly; I get 404 for any route on server

import os
from app import create_app

from flask_sqlalchemy import SQLAlchemy

app = create_app(os.getenv('FLASK_CONFIG') or 'default')


if os.path.exists('.env'):
		print('Importing environment from .env...')
		for line in open('.env'):
				var = line.strip().split('=')
				if len(var) == 2:
						os.environ[var[0]] = var[1]

if __name__ == "__main__":
    app.run(host='0.0.0.0')

"""
from app import create_app, db

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

migrate = Migrate(app, db)
manager = Manager(app)

if os.environ.get('APP_SETTINGS') == 'config.HerokuConfig':
	manager.add_command('runserver', Server(host='0.0.0.0', port=os.environ.get("PORT", 5000), threaded=True))

manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
		manager.run()
"""