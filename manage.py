import os

# COV = None
# if os.environ.get('FLASK_COVERAGE'):
# 		import coverage
# 		COV = coverage.coverage(branch=True, include='project/*')
# 		COV.start()

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

#	app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

if os.environ.get('APP_SETTINGS') == 'config.HerokuConfig':
	manager.add_command('runserver', Server(host='0.0.0.0', port=os.environ.get("PORT", 5000), threaded=True))

manager.add_command('db', MigrateCommand)



# def make_shell_context():
# 	from project.models import App, Asset, Function, Organization, Role, Schema, Site, Transaction, User, Grant, IdTanslation, MaintenanceEvent, Point, Template
# 	return dict(
# 		app=app, 
# 		db=db, 
# 		App=App, 
# 		Asset=Asset, 
# 		Function=Function, 
# 		Organization=Organization, 
# 		Role=Role, 
# 		Schema=Schema, 
# 		Site=Site, 
# 		Transaction=Transaction, 
# 		User=User, 
# 		Grant=Grant,
# 		IdTanslation=IdTanslation,
# 		MaintenanceEvent=MaintenanceEvent,
# 		Point=Point,
# 		Template=Template
# 	)

# manager.add_command("shell", Shell(make_context=make_shell_context))


# @manager.command
# def test(coverage=False):
# 		"""Run the unit tests."""
# 		if coverage and not os.environ.get('FLASK_COVERAGE'):
# 				import sys
# 				os.environ['FLASK_COVERAGE'] = '1'
# 				os.execvp(sys.executable, [sys.executable] + sys.argv)
# 		import unittest
# 		tests = unittest.TestLoader().discover('tests')
# 		unittest.TextTestRunner(verbosity=2).run(tests)
# 		if COV:
# 				COV.stop()
# 				COV.save()
# 				print('Coverage Summary:')
# 				COV.report()
# 				basedir = os.path.abspath(os.path.dirname(__file__))
# 				covdir = os.path.join(basedir, 'tmp/coverage')
# 				COV.html_report(directory=covdir)
# 				print('HTML version: file://%s/index.html' % covdir)
# 				COV.erase()


# @manager.command
# def profile(length=25, profile_dir=None):
# 		"""Start the application under the code profiler."""
# 		from werkzeug.contrib.profiler import ProfilerMiddleware
# 		app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
# 																			profile_dir=profile_dir)
# 		app.run()


@manager.command
def deploy():
		"""Run deployment tasks."""
		from flask_migrate import upgrade


		# migrate database to latest revision
		upgrade()

		"""
		from project.models import RoleHolder, App, Asset, Function, Grant, IdTranslation, Organization, Point, Role, Schema, Site, Transaction, User
		from project.utils.test_schemas import test_schemas
		schema_list = []
		schema_dict = {}
		for k, v in test_schemas.items():
			s = Schema({"name": k, "value": v})
			schema_list.append(s)
			schema_dict[k] = s

		db.session.add_all(schema_list)
		db.session.commit()
		"""

if __name__ == '__main__':
		manager.run()
