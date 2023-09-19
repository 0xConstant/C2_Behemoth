from app import celery, db, app
from application.models import Users
from utilities.wallet_api import wallet_balance
from datetime import datetime
from celery.schedules import crontab
import pytz
from datetime import timedelta


tz = pytz.timezone('America/Toronto')


@celery.task
def terminate_user(id):
    """
    This task is used for deleting a user's records (keys) after their expiration time hits.
    :param id:
    :return:
    """
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
    """
    This task is used for checking funds of each Monero account balance for every user to verify funds.
    It's setup with Celery beat to run every 1 minute, modify this if you face performance issues.
    :return:
    """
    with app.app_context():
        users = Users.query.all()
        for user in users:
            try:
                balance = wallet_balance(user.address_index)
                if balance > 0:
                    user.amount_paid = balance
                    if balance >= user.total_payment and user.pic_id:
                        user.status = True
                        user.payment_date = datetime.now(tz=tz)
            except Exception as e:
                print(e)
            db.session.commit()


@celery.task
def update_payments():
    with app.app_context():
        current_time = datetime.now().astimezone().replace(tzinfo=None)
        users = Users.query.all()

        for user in users:
            time_difference = current_time - user.creation_date
            increments = time_difference.total_seconds() // (2 * 60)
            user.total_payment += 30 * increments
            user.payment_increase += increments

        db.session.commit()


celery.conf.beat_schedule = {
    "check-wallet": {
        'task': 'application.tasks.check_wallet',
        'schedule': crontab(minute='*/1')
    }
}


celery.conf.beat_schedule = {
    'increase-payment': {
        'task': 'application.tasks.update_payments',
        'schedule': crontab(minute='*/1'),
    },
}
