from faker import Faker
from app import db, app
from application.models import Users
from datetime import datetime, timedelta
from utilities.gen_uid import pic_id

# Instantiate faker
fake = Faker()


def generate_dummy_user():
    current_time = datetime.now().astimezone()
    expiration_date = current_time + timedelta(hours=8)

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
    pic_uid = pic_id(3)

    user = Users(
        username=username,
        hostname=hostname,
        uid=uid,
        email=email,
        ip_address=ip_address,
        pic_uid=pic_uid,
        public_key=public_key,
        private_key=private_key,
        crypto_address=crypto_address,
        total_payment=payment,
        creation_date=current_time,
        address_index=address_index,
        expiration=expiration_date
    )

    # Add and commit the user to the database
    db.session.add(user)
    db.session.commit()

    print(f"Added dummy user with UID: {uid}")


with app.app_context():
    generate_dummy_user()
