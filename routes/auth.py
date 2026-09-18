from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user
from models import Patient, Doctor

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = Patient.query.filter_by(email=email).first() or Doctor.query.filter_by(email=email).first()
        if user and user.check_password(password):
            login_user(user)
            flash("Logged in successfully!")
            return redirect(url_for('patient.dashboard' if isinstance(user, Patient) else 'doctor.dashboard'))
        else:
            flash("Invalid credentials.")
    return render_template('login.html')

@auth_bp.route('/logout')
def logout():
    logout_user()
    flash("Logged out.")
    return redirect(url_for('auth.login'))
