from app import celery, db, app
from application.models import Users


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


