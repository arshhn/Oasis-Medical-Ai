from flask_sqlalchemy import SQLAlchemy
from datetime import date
db = SQLAlchemy()


class Patient(db.Model):
    __bind_key__ = 'patients'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    # .set_password and .check_password methods as shown earlier
    # Editable fields
    address = db.Column(db.String(200))
    state = db.Column(db.String(50))
    blood_group = db.Column(db.String(5))
    physically_challenged = db.Column(db.Boolean, default=False)
    photo = db.Column(db.String(200))  # Filepath or URL

class Doctor(db.Model):
    __bind_key__ = 'doctors'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    specialization = db.Column(db.String(100), nullable=False)
    qualifications = db.Column(db.String(200))                   
    phone = db.Column(db.String(20), nullable=False)
    gender = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    # .set_password and .check_password methods as shown earlier
    # Editable fields
    address = db.Column(db.String(200))
    state = db.Column(db.String(50))
    blood_group = db.Column(db.String(5))
    physically_challenged = db.Column(db.Boolean, default=False)
    photo = db.Column(db.String(200))  # Filepath or URL
    
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey('patient.id'), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey('doctor.id'), nullable=False)
    appointment_date = db.Column(db.Date, nullable=False)
    reason = db.Column(db.String(300))
    status = db.Column(db.String(50), default='Scheduled')  # e.g. Scheduled, Completed, Canceled
    disease = db.Column(db.Text)  # Add this field for diagnosis or doctor's notes


    

