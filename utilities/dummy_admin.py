from app import app, db
from application.models import Administrator

admin = Administrator(username="constant")
admin.set_password("constant")

with app.app_context():
	db.session.add(admin)
	db.session.commit()
