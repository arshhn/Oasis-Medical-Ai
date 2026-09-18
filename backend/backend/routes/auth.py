from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user
from models import Patient, Doctor

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        # Check doctor
        user = Doctor.query.filter_by(email=email).first()
        if not user:
            user = Patient.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user)
            flash("Login successful!", "success")
            return redirect(url_for("patient.dashboard"))  # or doctor dashboard

        flash("Invalid email or password", "danger")

    return render_template("login.html")
