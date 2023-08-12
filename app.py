from flask import Flask, g
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from datetime import timedelta
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import warnings


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///behemoth.db'
app.config['REMEMBER_COOKIE_DURATION'] = timedelta(hours=1)
db = SQLAlchemy(app)

with warnings.catch_warnings():                             # replace this with redis in the future
    warnings.simplefilter("ignore")
    limiter = Limiter(key_func=get_remote_address, app=app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = "EhYnSGGYwrjFlOJ0Md4PpKqGBv1ZaPti"
csrf = CSRFProtect(app)


@app.before_request
def before_request():
    g.notifications_count = 10





from application.models import Users
from application import views

with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(ssl_context='adhoc', host="0.0.0.0")

