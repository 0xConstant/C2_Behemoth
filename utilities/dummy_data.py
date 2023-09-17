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
    uid = fake.uuid4()  # Assuming uid is a UUID
    email = fake.email()
    ip_address = fake.ipv4()
    public_key = fake.sha256()  # This is just an example, adjust as needed
    private_key = fake.sha256()  # This is just an example, adjust as needed
    crypto_address = fake.sha256()  # This is just an example, adjust as needed
    payment = 100
    status = False
    amount_paid = 0
    address_index = fake.random_digit()  # Assuming it's a random single digit; adjust as needed

    # Create a new user with the generated dummy data
    user = Users(
        username=username,
        hostname=hostname,
        uid=uid,
        email=email,
        ip_address=ip_address,
        public_key=public_key,
        private_key=private_key,
        crypto_address=crypto_address,
        status=status,
        total_payment=payment,
        amount_paid=amount_paid,
        address_index=address_index,
        expiration=expiration_date
    )

    # Add and commit the user to the database
    db.session.add(user)
    db.session.commit()

    print(f"Added dummy user with UID: {uid}")


with app.app_context():
    generate_dummy_user()
