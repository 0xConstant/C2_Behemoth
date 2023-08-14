from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from application.utils import human_readable_date
from celery import Celery

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://roger:jackass#XX1717@localhost/behemoth'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)
app.config['CELERY_BROKER_URL'] = "redis://:jackass%23XX1717@localhost:6379/0"
app.config['CELERY_RESULT_BACKEND'] = "redis://:jackass%23XX1717@localhost:6379/0"

db = SQLAlchemy(app)
app.jinja_env.globals.update(human_readable_date=human_readable_date)

limiter = Limiter(
	key_func=get_remote_address,
	app=app,
	storage_uri="redis://:jackass%23XX1717@localhost:6379/0",
)


# Celery instance creation
def make_celery(app):
	celery = Celery(
		app.import_name,
		backend=app.config['CELERY_RESULT_BACKEND'],
		broker=app.config['CELERY_BROKER_URL']
	)
	celery.conf.update(app.config)

	class ContextTask(celery.Task):
		def __call__(self, *args, **kwargs):
			with app.app_context():
				return self.run(*args, **kwargs)

	celery.Task = ContextTask

	return celery


celery = make_celery(app)


# Example Celery Task (can be moved to another module like tasks.py)
@celery.task
def add_together(a, b):
	return a + b


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = "EhYnSGGYwrjFlOJ0Md4PpKqGBv1ZaPti"
csrf = CSRFProtect(app)

from application.models import Users
from application import views

with app.app_context():
	db.create_all()

if __name__ == '__main__':
	app.run()
