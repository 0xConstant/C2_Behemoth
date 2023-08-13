from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, login_required, logout_user
from application.models import *
from utilities.gen_rsa import gen_keys
import random, string
from app import login_manager, csrf, limiter
from werkzeug.security import check_password_hash
from application.forms import LoginForm
from application.models import Users, UsersPaid


@app.route("/new-user", methods=["POST"])
@csrf.exempt
def new_user():
    try:
        data = request.json
        keys = gen_keys()
        new_user = Users(
            username=data.get("Username"),
            hostname=data.get("Hostname"),
            uid=data.get("UID"),
            os_name=data.get("OS"),
            os_version=data.get("Version"),
            os_architecture=data.get("Architecture"),
            email=data.get("User Email"),
            public_key=keys[1],
            private_key=keys[0],
            crypto_address=''.join(random.choices(string.ascii_letters + string.digits, k=16)),
            total_payment=100,
            status=False,
            amount_paid=0
        )

        db.session.add(new_user)
        db.session.commit()

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


@login_required
@app.route("/dashboard", methods=["GET", "POST"])
def dashboard():
    return render_template("dashboard/dashboard.html", active_page='dashboard')


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
