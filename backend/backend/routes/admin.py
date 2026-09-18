from flask import Blueprint, render_template
from flask_login import login_required
from models import Doctor, Patient, Appointment

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/dashboard')
@login_required
def dashboard():
    doctor_count = Doctor.query.count()
    patient_count = Patient.query.count()
    appointment_count = Appointment.query.count()
    return render_template('admin_dashboard.html',
                           doctor_count=doctor_count,
                           patient_count=patient_count,
                           appointment_count=appointment_count)

# Add more views/CRUD as needed
