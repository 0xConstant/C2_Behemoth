from faker import Faker
from app import db, app
from application.models import Users
from datetime import datetime, timedelta


# Instantiate faker
fake = Faker()


def generate_dummy_user():
    tz = datetime.now().astimezone().tzinfo
    expiration_date = datetime.now(tz=tz) + timedelta(hours=8)

    username = fake.user_name()
    hostname = fake.hostname()
    uid = fake.uuid4()
    email = fake.email()
    ip_address = fake.ipv4()
    public_key = fake.sha256()
    private_key = fake.sha256()
    crypto_address = fake.sha256()
    payment = 100
    address_index = fake.random_digit()

    user = Users(
        username=username,
        hostname=hostname,
        uid=uid,
        email=email,
        ip_address=ip_address,
        public_key=public_key,
        private_key=private_key,
        crypto_address=crypto_address,
        total_payment=payment,
        address_index=address_index,
        expiration=expiration_date
    )

    # Add and commit the user to the database
    db.session.add(user)
    db.session.commit()

    print(f"Added dummy user with UID: {uid}")


with app.app_context():
    generate_dummy_user()
