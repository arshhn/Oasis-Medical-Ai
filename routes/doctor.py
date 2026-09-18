from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from models import db, Doctor, Appointment, Patient
from forms import DoctorSignupForm, ProfileUpdateForm, AppointmentUpdateForm
from datetime import date
from sqlalchemy import func

doctor_bp = Blueprint('doctor', __name__, url_prefix='/doctor')

@doctor_bp.route('/dashboard')
@login_required
def dashboard():
    # Query upcoming appointments (today or future dates)
    upcoming_appts = Appointment.query.filter(
        Appointment.doctor_id == current_user.id,
        Appointment.appointment_date >= date.today()
    ).order_by(Appointment.appointment_date.asc()).all()

    # Prepare appointment details with patient info
    detailed_appts = []
    for appt in upcoming_appts:
        patient = Patient.query.get(appt.patient_id)
        detailed_appts.append({
            'id': appt.id,
            'date': appt.appointment_date.strftime('%Y-%m-%d'),
            'patient_name': patient.name if patient else "Unknown",
            'reason': appt.reason,
            'status': getattr(appt, 'status', ""),
            'disease': getattr(appt, 'disease', "")
        })
    return render_template('doctor_dashboard.html', upcoming_appointments=detailed_appts)

@doctor_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = DoctorSignupForm()
    if form.validate_on_submit():
        doctor = Doctor(
            name=form.name.data,
            specialization=form.specialization.data,
            qualifications=form.qualifications.data,
            phone=form.phone.data,
            gender=form.gender.data,
            email=form.email.data
        )
        doctor.set_password(form.password.data)
        db.session.add(doctor)
        db.session.commit()
        flash('Doctor registered successfully!')
        return redirect(url_for('doctor.signup'))
    return render_template('doctor_signup.html', form=form)

@doctor_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = Doctor.query.get(current_user.id)
    form = ProfileUpdateForm(obj=user)
    if form.validate_on_submit():
        user.address = form.address.data
        user.state = form.state.data
        user.blood_group = form.blood_group.data
        user.physically_challenged = form.physically_challenged.data
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('doctor.profile'))
    return render_template('doctor_profile.html', user=user, form=form)

@doctor_bp.route('/appointments')
@login_required
def appointments():
    # Fetch all appointments for the logged-in doctor (most recent first)
    appts = Appointment.query.filter_by(doctor_id=current_user.id).order_by(Appointment.appointment_date.desc()).all()
    detailed_appts = []
    for appt in appts:
        patient = Patient.query.get(appt.patient_id)
        detailed_appts.append({
            'appointment': appt,
            'patient': patient
        })
    return render_template('doctor_appointments.html', appointments=detailed_appts)

@doctor_bp.route('/update_appointment/<int:appointment_id>', methods=['GET', 'POST'])
@login_required
def update_appointment(appointment_id):
    appt = Appointment.query.get_or_404(appointment_id)
    form = AppointmentUpdateForm(obj=appt)
    if form.validate_on_submit():
        appt.status = form.status.data
        if form.status.data == 'Rescheduled' and form.new_date.data:
            appt.appointment_date = form.new_date.data
        appt.disease = form.disease.data
        db.session.commit()
        flash('Appointment updated successfully.')
        return redirect(url_for('doctor.dashboard'))
    return render_template('update_appointment.html', form=form, appt=appt)

@doctor_bp.route('/analytics')
@login_required
def analytics():
    # Daily appointment counts for this week
    daily_stats = (
        db.session.query(
            func.strftime('%Y-%m-%d', Appointment.appointment_date),
            func.count()
        )
        .filter_by(doctor_id=current_user.id)
        .group_by(func.strftime('%Y-%m-%d', Appointment.appointment_date))
        .all()
    )
    # Monthly appointment counts for this year
    monthly_stats = (
        db.session.query(
            func.strftime('%Y-%m', Appointment.appointment_date),
            func.count()
        )
        .filter_by(doctor_id=current_user.id)
        .group_by(func.strftime('%Y-%m', Appointment.appointment_date))
        .all()
    )
    return render_template('doctor_analytics.html', daily_stats=daily_stats, monthly_stats=monthly_stats)
