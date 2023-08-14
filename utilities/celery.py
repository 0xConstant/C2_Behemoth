from celery import Celery
from app import app  # adjust the import based on your application structure

def make_celery(app):
    celery = Celery(
        app.import_name,
        backend=app.config['CELERY_RESULT_BACKEND'],
        broker=app.config['CELERY_BROKER_URL']
    )
    celery.conf.update(app.config)
    return celery


flask_app = app  # or however you create your Flask app instance
celery = make_celery(flask_app)
