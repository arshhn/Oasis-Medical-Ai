from flask_login import login_required, current_user
from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from models import db, Patient, Appointment, Doctor
from forms import PatientSignupForm, ProfileUpdateForm, AppointmentForm
from datetime import date

patient_bp = Blueprint('patient', __name__, url_prefix='/patient')

@patient_bp.route('/dashboard')
def dashboard():
    return "patient Dashboard Works!"

@patient_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form = PatientSignupForm()
    if form.validate_on_submit():
        patient = Patient(
            name=form.name.data,
            age=form.age.data,
            phone=form.phone.data,
            gender=form.gender.data,
            email=form.email.data
        )
        patient.set_password(form.password.data)
        db.session.add(patient)
        db.session.commit()
        flash('Patient registered successfully!')
        return redirect(url_for('patient.signup'))
    return render_template('patient_signup.html', form=form)

@patient_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    user = Patient.query.get(current_user.id)
    form = ProfileUpdateForm(obj=user)
    if form.validate_on_submit():
        user.address = form.address.data
        user.state = form.state.data
        user.blood_group = form.blood_group.data
        user.physically_challenged = form.physically_challenged.data
        db.session.commit()
        flash('Profile updated successfully')
        return redirect(url_for('patient.profile'))
    return render_template('patient_profile.html', user=user, form=form)

@patient_bp.route('/specializations', methods=['GET'])
def specializations():
    specs = db.session.query(Doctor.specialization).distinct().all()
    return jsonify([s[0] for s in specs])

@patient_bp.route('/doctors_by_field', methods=['GET'])
def doctors_by_field():
    field = request.args.get('field')
    doctors = Doctor.query.filter(Doctor.specialization == field).all()
    return jsonify([{'id': d.id, 'name': d.name, 'qualifications': d.qualifications} for d in doctors])

MAX_APPOINTMENTS_PER_DAY = 3

@patient_bp.route('/appointment', methods=['GET', 'POST'])
@login_required
def appointment():
    form = AppointmentForm()
    # Populate doctor choices dynamically
    form.doctor.choices = [(d.id, f"{d.name} ({d.qualifications})") for d in Doctor.query.all()]
    if form.validate_on_submit():
        appt_date = form.appointment_date.data
        if appt_date < date.today():
            flash("Cannot book appointment in the past.")
            return redirect(url_for('patient.appointment'))

        count = Appointment.query.filter_by(doctor_id=form.doctor.data, appointment_date=appt_date).count()
        if count >= MAX_APPOINTMENTS_PER_DAY:
            flash("Doctor is fully booked on this date. Choose another date or doctor.")
            return redirect(url_for('patient.appointment'))

        appt = Appointment(
            patient_id=current_user.id,
            doctor_id=form.doctor.data,
            appointment_date=appt_date,
            reason=form.reason.data
        )
        db.session.add(appt)
        db.session.commit()
        flash("Appointment booked successfully.")
        return redirect(url_for('patient.appointment'))

    return render_template('appointment.html', form=form)

@patient_bp.route('/analytics')
@login_required
def analytics():
    # Fetch all appointments of current patient with status and disease info
    appointments = Appointment.query.filter_by(patient_id=current_user.id).order_by(Appointment.appointment_date.desc()).all()

    # Prepare a list of appointment details to pass to template
    appt_list = []
    for appt in appointments:
        appt_list.append({
            'date': appt.appointment_date.strftime('%Y-%m-%d'),
            'status': getattr(appt, 'status', 'N/A'),
            'disease': getattr(appt, 'disease', 'No report yet'),
            'doctor_name': appt.doctor.name if appt.doctor else 'Unknown'
        })

    return render_template('patient_analytics.html', appointments=appt_list)
