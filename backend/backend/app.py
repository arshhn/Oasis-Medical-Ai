from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from models import db, Patient, Doctor  # your existing models

# Import Blueprints
from routes.patient import patient_bp
from routes.doctor import doctor_bp
from routes.admin import admin_bp
from routes.auth import auth_bp
from routes.upload import upload_bp

# ---------------------------------------------------------
# APP INITIALIZATION
# ---------------------------------------------------------
app = Flask(__name__)
app.config['SECRET_KEY'] = "oasis-secret-key"
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///oasis.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# ---------------------------------------------------------
# LOGIN MANAGER
# ---------------------------------------------------------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "auth.login"   # Redirect unauthorized users to login page


@login_manager.user_loader
def load_user(user_id):
    # A user can be either a Patient or a Doctor
    user = Patient.query.get(user_id)
    if not user:
        user = Doctor.query.get(user_id)
    return user


# ---------------------------------------------------------
# BLUEPRINT REGISTRATION
# ---------------------------------------------------------
app.register_blueprint(patient_bp)
app.register_blueprint(doctor_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(upload_bp)

# ---------------------------------------------------------
# HOME ROUTE
# ---------------------------------------------------------
@app.route("/")
def home():
    return render_template("home.html")  # optional home page


# ---------------------------------------------------------
# RUN SERVER
# ---------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Creates DB if not exists
    app.run(debug=True)
