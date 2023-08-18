from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from application.utils import human_readable_date
from celery import Celery
from dotenv import load_dotenv
from os import environ


app = Flask(__name__)

load_dotenv()

app.config['SQLALCHEMY_DATABASE_URI'] = environ.get("DATABASE_URL")
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)
app.config["broker_url"] = environ.get("REDIS_URL")
app.config["result_backend"] = environ.get("REDIS_URL")

db = SQLAlchemy(app)

app.jinja_env.globals.update(human_readable_date=human_readable_date)

celery = Celery(app.name, broker=app.config["broker_url"])
celery.conf.update(app.config)


limiter = Limiter(
    key_func=get_remote_address,
    app=app,
    storage_uri=environ.get("REDIS_URL"),
)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = environ.get("SECRET_KEY")
csrf = CSRFProtect(app)


from application.models import Users
from application import views

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run()
