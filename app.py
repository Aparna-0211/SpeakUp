from flask import (
    Flask,
    render_template,
    request,
    jsonify,
    session,
    redirect,
    url_for
)

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)


# =========================
# FLASK APPLICATION
# =========================

app = Flask(__name__)


# =========================
# APPLICATION CONFIGURATION
# =========================

app.config["SECRET_KEY"] = "speakup-development-secret-key"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///speakup.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


# =========================
# DATABASE
# =========================

db = SQLAlchemy(app)


# =========================
# USER MODEL
# =========================

class User(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    username = db.Column(
        db.String(80),
        unique=True,
        nullable=False
    )

    email = db.Column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.Column(
        db.String(255),
        nullable=False
    )


# =========================
# CREATE DATABASE
# =========================

with app.app_context():

    db.create_all()


# =========================
# HOME PAGE
# =========================

@app.route("/")
def home():

    return render_template(
        "home.html"
    )


# =========================
# SIGN UP
# =========================

@app.route(
    "/signup",
    methods=["GET", "POST"]
)
def signup():

    if request.method == "POST":

        username = request.form["username"]

        email = request.form["email"]

        password = request.form["password"]


        # Check username

        existing_username = User.query.filter_by(
            username=username
        ).first()


        if existing_username:

            return "Username already exists."


        # Check email

        existing_email = User.query.filter_by(
            email=email
        ).first()


        if existing_email:

            return "Email already registered."


        # Hash password

        hashed_password = generate_password_hash(
            password
        )


        # Create user

        new_user = User(

            username=username,

            email=email,

            password=hashed_password

        )


        db.session.add(
            new_user
        )

        db.session.commit()


        return "Account created successfully!"


    return render_template(
        "signup.html"
    )


# =========================
# LOGIN
# =========================

@app.route(
    "/login",
    methods=["GET", "POST"]
)
def login():

    if request.method == "POST":

        email = request.form["email"]

        password = request.form["password"]


        # Find user

        user = User.query.filter_by(
            email=email
        ).first()


        # Verify password

        if user and check_password_hash(
            user.password,
            password
        ):

            # Store login information
            # inside Flask session

            session["user_id"] = user.id

            session["username"] = user.username

            session["email"] = user.email


            # Go to dashboard

            return redirect(
                url_for("dashboard")
            )


        return "Invalid email or password."


    return render_template(
        "login.html"
    )


# =========================
# DASHBOARD
# =========================

@app.route("/dashboard")
def dashboard():

    # Check if user is logged in

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    username = session.get(
        "username"
    )


    return render_template(

        "dashboard.html",

        username=username

    )


# =========================
# CHECK-IN PAGE
# =========================

@app.route("/checkin")
def checkin():

    # Only logged-in users
    # can access check-in

    if "user_id" not in session:

        return redirect(
            url_for("login")
        )


    return render_template(
        "checkin.html"
    )


# =========================
# CHECK-IN API
# =========================

@app.route(
    "/api/checkin",
    methods=["POST"]
)
def submit_checkin():

    # Make sure user is logged in

    if "user_id" not in session:

        return jsonify({

            "success": False,

            "message": "Please log in first."

        }), 401


    data = request.get_json()


    situation = data.get(
        "situation",
        ""
    )


    feeling = data.get(
        "feeling",
        ""
    )


    confidence = data.get(
        "confidence",
        ""
    )


    reflection = data.get(
        "reflection",
        ""
    )


    # For now we only receive
    # the check-in data.
    #
    # We will connect this to
    # SQLite in the next stage.


    return jsonify({

        "success": True,

        "message": "Your check-in was received!",

        "data": {

            "situation": situation,

            "feeling": feeling,

            "confidence": confidence,

            "reflection": reflection

        }

    })


# =========================
# LOGOUT
# =========================

@app.route("/logout")
def logout():

    # Remove all session data

    session.clear()


    # Return to login

    return redirect(
        url_for("login")
    )


# =========================
# RUN APPLICATION
# =========================

if __name__ == "__main__":

    app.run(
        debug=True,
        port=5001
    )
    